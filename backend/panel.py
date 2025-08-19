from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .db import db
from .models import User, Producto, RegistroEntrada, RegistroSalida
from werkzeug.security import check_password_hash

panel = Blueprint('panel', __name__)

@panel.get('/panel/login')
def login_panel():
    return render_template('panel_login.html')

@panel.post('/panel/login')
def do_login_panel():
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    user = db.session.scalar(db.select(User).where(User.email==email))
    if not user or not user.check_password(password):
        return render_template('panel_login.html', error='Credenciales inválidas')
    session['panel_user_id'] = user.id
    return redirect(url_for('panel.dashboard'))

@panel.get('/panel/logout')
def logout_panel():
    session.pop('panel_user_id', None)
    return redirect(url_for('panel.login_panel'))

@panel.get('/panel')
def dashboard():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel.login_panel'))
    productos = db.session.scalars(db.select(Producto).order_by(Producto.nombre)).all()
    return render_template('panel_dashboard.html', productos=productos)

@panel.post('/panel/productos')
def crear_producto_panel():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel.login_panel'))
    nombre = (request.form.get('nombre') or '').strip()
    stock_minimo = int(request.form.get('stock_minimo') or 0)
    detalle = request.form.get('detalle') or None
    categoria = request.form.get('categoria') or None

    if not nombre:
        flash('El nombre es obligatorio', 'danger')
        return redirect(url_for('panel.dashboard'))

    if db.session.scalar(db.select(Producto).where(Producto.nombre==nombre)):
        flash('Ya existe un producto con ese nombre', 'warning')
        return redirect(url_for('panel.dashboard'))

    p = Producto(nombre=nombre, stock_minimo=stock_minimo, detalle=detalle, categoria=categoria)
    db.session.add(p)
    db.session.commit()
    flash('Producto creado', 'success')
    return redirect(url_for('panel.dashboard'))

@panel.post('/panel/stock/entrada')
def entrada_panel():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel.login_panel'))
    producto_id = int(request.form.get('producto_id'))
    cantidad = int(request.form.get('cantidad') or 0)
    obs = request.form.get('observaciones')
    p = db.session.get(Producto, producto_id)
    if not p or cantidad<=0:
        flash('Datos inválidos', 'danger')
        return redirect(url_for('panel.dashboard'))
    mov = RegistroEntrada(producto_id=producto_id, cantidad=cantidad, observaciones=obs, usuario_id=session['panel_user_id'])
    p.stock_actual += cantidad
    db.session.add(mov)
    db.session.commit()
    flash('Entrada registrada', 'success')
    return redirect(url_for('panel.dashboard'))

@panel.post('/panel/stock/salida')
def salida_panel():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel.login_panel'))
    producto_id = int(request.form.get('producto_id'))
    cantidad = int(request.form.get('cantidad') or 0)
    obs = request.form.get('observaciones')
    p = db.session.get(Producto, producto_id)
    if not p or cantidad<=0 or p.stock_actual < cantidad:
        flash('Datos inválidos o stock insuficiente', 'danger')
        return redirect(url_for('panel.dashboard'))
    mov = RegistroSalida(producto_id=producto_id, cantidad=cantidad, observaciones=obs, usuario_id=session['panel_user_id'])
    p.stock_actual -= cantidad
    db.session.add(mov)
    db.session.commit()
    flash('Salida registrada', 'success')
    return redirect(url_for('panel.dashboard'))
