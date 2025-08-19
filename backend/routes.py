from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from sqlalchemy import func
import os

from .db import db
from .models import User, Producto, RegistroEntrada, RegistroSalida
from .utils import admin_required

api_bp = Blueprint('api', __name__)

@api_bp.get("/")
def api_root():
    return jsonify({"service": "specialwash-backend", "api": "/api", "ok": True})

# Auth
@api_bp.post("/auth/seed-admin")
def seed_admin():
    existing = db.session.scalar(db.select(func.count()).select_from(User))
    if existing and existing > 0:
        return jsonify({"created": False, "reason": "Ya existe un usuario. Usa /auth/login."}), 400

    email = os.getenv("ADMIN_EMAIL", "admin@specialwash.local").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "admin12345")

    u = User(email=email, role="admin")
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    return jsonify({"created": True, "email": email})

@api_bp.get("/auth/admin-exists")
def admin_exists():
    count = db.session.scalar(db.select(func.count()).select_from(User))
    return jsonify({"admin_exists": count > 0})

@api_bp.post("/auth/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.session.scalar(db.select(User).where(User.email == email))
    if not user or not user.check_password(password):
        return jsonify({"msg": "Email o contraseña incorrectos"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email}
    )
    return jsonify({"access_token": access_token, "role": user.role, "email": user.email})

# Productos
@api_bp.post("/productos")
@admin_required
def crear_producto():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"msg": "nombre es obligatorio"}), 400

    if db.session.scalar(db.select(Producto).where(Producto.nombre == nombre)):
        return jsonify({"msg": "Ya existe un producto con ese nombre"}), 409

    p = Producto(
        nombre=nombre,
        detalle=data.get("detalle"),
        categoria=data.get("categoria"),
        stock_minimo=int(data.get("stock_minimo") or 0),
        stock_actual=int(data.get("stock_actual") or 0),
        activo=True,
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"msg": "Producto creado", "producto": serialize_producto(p)}), 201

@api_bp.get("/productos")
@admin_required
def listar_productos():
    productos = db.session.scalars(db.select(Producto).order_by(Producto.nombre)).all()
    return jsonify([serialize_producto(p) for p in productos])

@api_bp.put("/productos/<int:pid>")
@admin_required
def editar_producto(pid):
    p = db.session.get(Producto, pid)
    if not p:
        return jsonify({"msg": "Producto no encontrado"}), 404

    data = request.get_json() or {}

    if "nombre" in data:
        nombre = (data["nombre"] or "").strip()
        if not nombre:
            return jsonify({"msg": "nombre no puede estar vacío"}), 400
        if nombre != p.nombre and db.session.scalar(db.select(Producto).where(Producto.nombre == nombre)):
            return jsonify({"msg": "Ya existe otro producto con ese nombre"}), 409
        p.nombre = nombre

    for field in ["detalle", "categoria"]:
        if field in data:
            setattr(p, field, data[field])

    if "stock_minimo" in data:
        p.stock_minimo = int(data["stock_minimo"] or 0)

    if "activo" in data:
        p.activo = bool(data["activo"])

    db.session.commit()
    return jsonify({"msg": "Producto actualizado", "producto": serialize_producto(p)})

@api_bp.delete("/productos/<int:pid>")
@admin_required
def eliminar_producto(pid):
    p = db.session.get(Producto, pid)
    if not p:
        return jsonify({"msg": "Producto no encontrado"}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({"msg": "Producto eliminado"})


def serialize_producto(p: Producto):
    return {
        "id": p.id,
        "nombre": p.nombre,
        "detalle": p.detalle,
        "categoria": p.categoria,
        "stock_minimo": p.stock_minimo,
        "stock_actual": p.stock_actual,
        "activo": p.activo,
        "alerta_bajo_stock": p.stock_actual <= p.stock_minimo if p.activo else False,
    }

# Stock
@api_bp.post("/stock/entrada")
@admin_required
def registrar_entrada():
    data = request.get_json() or {}
    producto_id = data.get("producto_id")
    cantidad = int(data.get("cantidad") or 0)
    if not producto_id or cantidad <= 0:
        return jsonify({"msg": "producto_id y cantidad (>0) son obligatorios"}), 400

    p = db.session.get(Producto, int(producto_id))
    if not p:
        return jsonify({"msg": "Producto no encontrado"}), 404

    user_id = _current_user_id()
    entrada = RegistroEntrada(
        producto_id=p.id,
        cantidad=cantidad,
        observaciones=data.get("observaciones"),
        usuario_id=user_id,
    )
    p.stock_actual += cantidad
    db.session.add(entrada)
    db.session.commit()
    return jsonify({"msg": "Entrada registrada", "producto": serialize_producto(p)}), 201

@api_bp.post("/stock/salida")
@admin_required
def registrar_salida():
    data = request.get_json() or {}
    producto_id = data.get("producto_id")
    cantidad = int(data.get("cantidad") or 0)
    if not producto_id or cantidad <= 0:
        return jsonify({"msg": "producto_id y cantidad (>0) son obligatorios"}), 400

    p = db.session.get(Producto, int(producto_id))
    if not p:
        return jsonify({"msg": "Producto no encontrado"}), 404

    if p.stock_actual - cantidad < 0:
        return jsonify({"msg": "No hay stock suficiente"}), 400

    user_id = _current_user_id()
    salida = RegistroSalida(
        producto_id=p.id,
        cantidad=cantidad,
        observaciones=data.get("observaciones"),
        usuario_id=user_id,
    )
    p.stock_actual -= cantidad
    db.session.add(salida)
    db.session.commit()
    return jsonify({"msg": "Salida registrada", "producto": serialize_producto(p)}), 201

@api_bp.get("/stock")
@admin_required
def ver_stock():
    productos = db.session.scalars(db.select(Producto).where(Producto.activo == True).order_by(Producto.nombre)).all()
    return jsonify([serialize_producto(p) for p in productos])

@api_bp.get("/stock/entradas")
@admin_required
def listar_entradas():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    query = db.select(RegistroEntrada).order_by(RegistroEntrada.fecha.desc())
    if desde:
        from datetime import datetime
        query = query.where(RegistroEntrada.fecha >= datetime.strptime(desde, "%Y-%m-%d"))
    if hasta:
        from datetime import datetime
        dt = datetime.strptime(hasta, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.where(RegistroEntrada.fecha <= dt)
    entradas = db.session.scalars(query).all()
    return jsonify([_serialize_mov_e(e) for e in entradas])

@api_bp.get("/stock/salidas")
@admin_required
def listar_salidas():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    query = db.select(RegistroSalida).order_by(RegistroSalida.fecha.desc())
    if desde:
        from datetime import datetime
        query = query.where(RegistroSalida.fecha >= datetime.strptime(desde, "%Y-%m-%d"))
    if hasta:
        from datetime import datetime
        dt = datetime.strptime(hasta, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.where(RegistroSalida.fecha <= dt)
    salidas = db.session.scalars(query).all()
    return jsonify([_serialize_mov_s(s) for s in salidas])

# Helpers
from flask_jwt_extended import get_jwt_identity

def _serialize_mov_e(e: RegistroEntrada):
    return {
        "id": e.id,
        "producto_id": e.producto_id,
        "producto": e.producto.nombre if e.producto else None,
        "cantidad": e.cantidad,
        "fecha": e.fecha.isoformat(),
        "usuario_id": e.usuario_id,
        "observaciones": e.observaciones,
    }

def _serialize_mov_s(s: RegistroSalida):
    return {
        "id": s.id,
        "producto_id": s.producto_id,
        "producto": s.producto.nombre if s.producto else None,
        "cantidad": s.cantidad,
        "fecha": s.fecha.isoformat(),
        "usuario_id": s.usuario_id,
        "observaciones": s.observaciones,
    }

def _current_user_id():
    identity = get_jwt_identity()
    try:
        return int(identity)
    except Exception:
        return int(identity) if identity else None
