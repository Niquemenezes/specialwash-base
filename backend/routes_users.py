from flask import Blueprint, request, jsonify
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity
from .db import db
from .models import User
from .utils.authz import roles_required

users_bp = Blueprint("users", __name__)

@users_bp.get("/auth/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    u = db.session.get(User, int(uid)) if uid else None
    if not u:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    return jsonify({"id": u.id, "email": u.email, "role": u.role, "active": getattr(u, "active", True)})

@users_bp.get("/users")
@roles_required("admin")
def list_users():
    users = db.session.scalars(db.select(User).order_by(User.email)).all()
    return jsonify([{"id": u.id, "email": u.email, "role": u.role, "active": getattr(u, "active", True)} for u in users])

@users_bp.post("/users")
@roles_required("admin")
def create_user():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "staff").strip().lower()
    if role not in ("admin","staff"):
        return jsonify({"msg": "role debe ser 'admin' o 'staff'"}), 400
    if not email or not password:
        return jsonify({"msg": "email y password son obligatorios"}), 400
    if db.session.scalar(db.select(User).where(User.email == email)):
        return jsonify({"msg": "Ya existe un usuario con ese email"}), 409
    u = User(email=email, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return jsonify({"id": u.id, "email": u.email, "role": u.role}), 201

@users_bp.patch("/users/<int:uid>")
@roles_required("admin")
def update_user(uid):
    u = db.session.get(User, uid)
    if not u:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    data = request.get_json() or {}
    if "role" in data:
        role = (data["role"] or "").strip().lower()
        if role not in ("admin","staff"):
            return jsonify({"msg": "role inválido"}), 400
        u.role = role
    if "password" in data and data["password"]:
        u.set_password(data["password"])
    if "active" in data:
        setattr(u, "active", bool(data["active"]))
    db.session.commit()
    return jsonify({"msg": "Usuario actualizado"})

@users_bp.delete("/users/<int:uid>")
@roles_required("admin")
def delete_user(uid):
    u = db.session.get(User, uid)
    if not u:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    if hasattr(u, "active"):
        u.active = False
    else:
        db.session.delete(u)
    db.session.commit()
    return jsonify({"msg": "Usuario eliminado"})
