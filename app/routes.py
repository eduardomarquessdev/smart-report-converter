import json
import logging
import queue
import re
import threading
import time
import uuid
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from .converter import converter_txt_para_xlsx
from .jobs import finished_jobs, progress_queues

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


def _limpar_nome_saida(nome):
    nome = secure_filename(nome or "arquivo_final")
    nome = re.sub(r"\.xlsx$", "", nome, flags=re.IGNORECASE).strip("._ ")
    return nome or "arquivo_final"


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/converter", methods=["POST"])
def converter():
    f = request.files.get("arquivo")
    dest = request.form.get("destino", "").strip()
    nome = _limpar_nome_saida(request.form.get("nome", "arquivo_final"))

    if not f or not f.filename.lower().endswith(".txt"):
        return jsonify({"error": "Envie um arquivo .txt válido."}), 400

    filename = secure_filename(f.filename)
    if not filename.lower().endswith(".txt"):
        return jsonify({"error": "Nome de arquivo inválido."}), 400

    upload_dir = current_app.config["UPLOAD_DIR"]
    upload_dir.mkdir(parents=True, exist_ok=True)
    txt_path = upload_dir / f"{uuid.uuid4().hex}_{filename}"
    f.save(str(txt_path))

    if dest:
        saida_dir = Path(dest)
        try:
            saida_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            return jsonify({"error": "Não foi possível usar a pasta de destino informada."}), 400
    else:
        saida_dir = current_app.config["DEFAULT_OUTPUT_DIR"]
        saida_dir.mkdir(parents=True, exist_ok=True)

    saida = str(saida_dir / f"{nome}.xlsx")
    job_id = f"job_{uuid.uuid4().hex}"
    progress_queues[job_id] = queue.Queue()

    logger.info("Job %s iniciado (%s)", job_id, filename)

    t = threading.Thread(
        target=converter_txt_para_xlsx,
        args=(str(txt_path), saida, job_id),
        daemon=True,
    )
    t.start()

    return jsonify({"job_id": job_id})


@main_bp.route("/progresso/<job_id>")
def progresso(job_id):
    def generate():
        q = progress_queues.get(job_id)
        if not q:
            yield 'data: {"error": "Job nao encontrado"}\n\n'
            return
        while True:
            try:
                item = q.get(timeout=30)
                yield f"data: {json.dumps(item)}\n\n"
                if item.get("done") or item.get("error"):
                    progress_queues.pop(job_id, None)
                    break
            except queue.Empty:
                yield 'data: {"error": "Timeout"}\n\n'
                progress_queues.pop(job_id, None)
                break

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@main_bp.route("/download/<job_id>")
def download(job_id):
    # Importante: o download é resolvido a partir de um job_id que só existe
    # no servidor (gerado após uma conversão bem-sucedida), e não a partir de
    # um caminho de arquivo enviado pelo cliente. Isso evita que alguém
    # baixe arquivos arbitrários do servidor manipulando a URL.
    path = finished_jobs.get(job_id)
    if not path:
        return "Arquivo nao encontrado", 404

    import os
    if not os.path.exists(path):
        return "Arquivo nao encontrado", 404

    return send_file(path, as_attachment=True, download_name=os.path.basename(path))
