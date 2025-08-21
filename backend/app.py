import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .config import get_config
from .db import db
from .routes import api_bp  # <-- único blueprint público (API)

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # CORS solo para /api/*
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # Registrar solo la API
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    return app
