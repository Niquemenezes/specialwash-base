from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Producto(db.Model):
    __tablename__ = "producto"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    detalle = db.Column(db.String(255))
    categoria = db.Column(db.String(80))
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)
    stock_actual = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RegistroEntrada(db.Model):
    __tablename__ = "registro_entrada"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    producto = db.relationship('Producto', backref='entradas')
    usuario = db.relationship('User')

class RegistroSalida(db.Model):
    __tablename__ = "registro_salida"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    producto = db.relationship('Producto', backref='salidas')
    usuario = db.relationship('User')
