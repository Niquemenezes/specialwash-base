from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import jsonify, session, redirect, url_for

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role")
        if role != "admin":
            return jsonify({"msg": "Solo admin puede acceder"}), 403
        return fn(*args, **kwargs)
    return wrapper

# Autenticación sencilla para el panel (sesión)
def panel_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("panel_user_id"):
            return redirect(url_for("panel.login_panel"))
        return fn(*args, **kwargs)
    return wrapper
