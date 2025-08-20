from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from .config import get_config
from .db import db
from .routes import api_bp
from .superadmin import setup_superadmin
from .admin import admin_bp

load_dotenv()


def _fix_database_url(url: str) -> str:
    """
    Render suele dar DATABASE_URL con 'postgres://'.
    Para SQLAlchemy + psycopg3 forzamos el driver explícito 'postgresql+psycopg://'.
    """
    if not url:
        return ""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.split("://", 1)[1]
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def create_app():
    BASE_DIR = os.path.dirname(__file__)
    TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")
    STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

    app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
    app.config.from_object(get_config())
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config.setdefault("JSON_SORT_KEYS", False)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # --- Base de datos (Render -> DATABASE_URL) ---
    raw_db_url = os.getenv("DATABASE_URL", app.config.get("SQLALCHEMY_DATABASE_URI", ""))
    fixed_db_url = _fix_database_url(raw_db_url)
    if fixed_db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = fixed_db_url
    else:
        # fallback local para desarrollo
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///local.db"

    # --- CORS ---
    # Acepta cualquier Codespace por defecto; o lo que definas en CORS_ORIGINS
    origins_env = os.getenv("CORS_ORIGINS", r"https://.*\.app\.github\.dev")
    CORS(app, resources={r"/api/*": {"origins": origins_env}}, supports_credentials=True)

    # --- Extensiones ---
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # --- Blueprints ---
    app.register_blueprint(api_bp, url_prefix="/api")
    setup_superadmin(app)
    app.register_blueprint(admin_bp)

    # --- Rutas básicas / health ---
    @app.get("/")
    def root():
        return {"service": "specialwash-backend", "api": "/api", "ok": True}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/health")
    def api_health():
        return {"status": "ok"}

    # --- Errores JSON en /api ---
    @app.errorhandler(404)
    def not_found(e):
        if request.accept_mimetypes.accept_json or request.path.startswith("/api"):
            return jsonify({"error": "Not Found", "path": request.path}), 404
        return e

    @app.errorhandler(405)
    def method_not_allowed(e):
        if request.accept_mimetypes.accept_json or request.path.startswith("/api"):
            return jsonify({"error": "Method Not Allowed", "path": request.path}), 405
        return e

    # Importante: NO hacemos db.create_all() aquí; usa migraciones (flask db upgrade)
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
