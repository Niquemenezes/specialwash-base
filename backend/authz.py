import os
from functools import wraps
from flask import g, jsonify, session, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity as _get_jwt_identity

DISABLE_AUTH = os.getenv("DISABLE_AUTH", "0") == "1"

def optional_jwt_required(fn):
    """Si DISABLE_AUTH=1 no exige token; si no, verifica JWT."""
    @wraps(fn)
    def wrapper(*a, **kw):
        if DISABLE_AUTH:
            g.current_user = {"id": 1, "email": "admin@specialwash.es", "role": "administrador"}
            return fn(*a, **kw)
        verify_jwt_in_request()
        return fn(*a, **kw)
    return wrapper

def admin_required(fn):
    """Admin sólo cuando hay JWT activo; con DISABLE_AUTH=1 deja pasar."""
    @wraps(fn)
    def wrapper(*a, **kw):
        if DISABLE_AUTH:
            g.current_user = {"id": 1, "email": "admin@specialwash.es", "role": "administrador"}
            return fn(*a, **kw)
        verify_jwt_in_request()
        claims = get_jwt() or {}
        role = (claims.get("role") or claims.get("rol") or (claims.get("identity") or {}).get("role") or "").lower()
        if role not in {"admin", "administrador", "hotel"}:
            return jsonify({"msg": "Solo admin puede acceder"}), 403
        return fn(*a, **kw)
    return wrapper

def get_identity():
    """Identidad fake si DISABLE_AUTH=1; si no, la real del JWT."""
    if DISABLE_AUTH:
        return {"id": 1, "email": "admin@specialwash.es", "role": "administrador"}
    try:
        return _get_jwt_identity()
    except Exception:
        return {}

def panel_required(fn):
    """Protección del panel por sesión; con DISABLE_AUTH=1 se omite."""
    @wraps(fn)
    def wrapper(*a, **kw):
        if DISABLE_AUTH:
            return fn(*a, **kw)
        if not session.get("panel_user_id"):
            return redirect(url_for("panel.login_panel"))
        return fn(*a, **kw)
    return wrapper
