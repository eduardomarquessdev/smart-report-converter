import os
from pathlib import Path


class Config:
    """Configuração da aplicação, lida a partir de variáveis de ambiente."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")

    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB

    # Pasta onde os .txt enviados pelo usuário são guardados temporariamente.
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(Path.home() / "conversor_uploads")))

    # Pasta padrão de saída, usada quando o usuário não informa um destino
    # customizado no formulário.
    DEFAULT_OUTPUT_DIR = Path(os.getenv("DEFAULT_OUTPUT_DIR", str(Path.home() / "Documents")))
