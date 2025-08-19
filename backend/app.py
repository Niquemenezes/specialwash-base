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

def create_app():
    BASE_DIR = os.path.dirname(__file__)
    TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")
    STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

    app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
    app.config.from_object(get_config())
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # ✅ CORS para permitir frontend desde cualquier subdominio GitHub Codespace
    CORS(app, resources={r"/api/*": {"origins": r"https://.*\.app\.github\.dev"}}, supports_credentials=True)

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # ✅ Blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    setup_superadmin(app)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def root():
        return {"service": "specialwash-backend", "api": "/api", "ok": True}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/health")
    def api_health():
        return {"status": "ok"}

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

    with app.app_context():
        db.create_all()

    return app

# ✅ Crear la app final
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
