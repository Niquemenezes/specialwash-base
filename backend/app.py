from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from .config import get_config
from .db import db
from .routes import api_bp
from .compat import compat_bp

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # API real
    app.register_blueprint(api_bp, url_prefix="/api")
    # Compat: acepta /auth, /productos, /stock sin /api y redirige con 307
    app.register_blueprint(compat_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.get("/")
    def root():
        return jsonify({"name": "SpecialWash API", "docs": "/api/health"}), 200

    return app
