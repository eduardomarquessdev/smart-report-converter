import logging
import os

from flask import Flask

from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    _configure_logging(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    if app.config["SECRET_KEY"] == "dev-only-change-me":
        app.logger.warning(
            "FLASK_SECRET_KEY não foi definida — usando valor padrão de "
            "desenvolvimento. Defina a variável de ambiente FLASK_SECRET_KEY."
        )

    return app


def _configure_logging(app):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    app.logger.addHandler(console_handler)
