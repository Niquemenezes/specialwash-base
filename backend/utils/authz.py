from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def roles_required(*roles):
    """
    Permite acceso sólo si el JWT contiene un 'role' incluido en roles.
    Uso: @roles_required("admin")  o  @roles_required("admin","staff")
    """
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            role = claims.get("role")
            if role not in roles:
                return jsonify({"msg": "Forbidden: role not allowed"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return deco
