
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .db import db
from .models import User, Producto, RegistroEntrada, RegistroSalida

admin_bp = Blueprint('panel_admin', __name__)

@admin_bp.get('/admin/login')
def login_admin():
    return render_template('admin_login.html')

@admin_bp.post('/admin/login')
def do_login_admin():
    email = (request.form.get('email') or '').strip().lower()
    password = request.form.get('password') or ''
    user = db.session.scalar(db.select(User).where(User.email==email))
    if not user or not user.check_password(password):
        return render_template('admin_login.html', error='Credenciales inválidas')
    session['panel_user_id'] = user.id
    return redirect(url_for('panel_admin.index_admin'))

@admin_bp.get('/admin/logout')
def logout_admin():
    session.pop('panel_user_id', None)
    return redirect(url_for('panel_admin.login_admin'))

@admin_bp.get('/admin')
def index_admin():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    productos = db.session.scalars(db.select(Producto).order_by(Producto.nombre)).all()
    entradas = db.session.scalars(
        db.select(RegistroEntrada).order_by(RegistroEntrada.fecha.desc()).limit(10)
    ).all()
    salidas = db.session.scalars(
        db.select(RegistroSalida).order_by(RegistroSalida.fecha.desc()).limit(10)
    ).all()
    return render_template('admin_index.html', productos=productos, entradas=entradas, salidas=salidas)

@admin_bp.post('/admin/productos')
def crear_producto_admin():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    nombre = (request.form.get('nombre') or '').strip()
    stock_minimo = int(request.form.get('stock_minimo') or 0)
    detalle = request.form.get('detalle') or None
    categoria = request.form.get('categoria') or None
    if not nombre:
        flash('El nombre es obligatorio', 'danger'); return redirect(url_for('panel_admin.index_admin'))
    if db.session.scalar(db.select(Producto).where(Producto.nombre==nombre)):
        flash('Ya existe un producto con ese nombre', 'warning'); return redirect(url_for('panel_admin.index_admin'))
    p = Producto(nombre=nombre, stock_minimo=stock_minimo, detalle=detalle, categoria=categoria)
    db.session.add(p); db.session.commit()
    flash('Producto creado', 'success'); return redirect(url_for('panel_admin.index_admin'))

@admin_bp.get('/admin/productos/<int:pid>/edit')
def editar_producto_form(pid:int):
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    p = db.session.get(Producto, pid)
    if not p:
        flash('Producto no encontrado', 'danger'); return redirect(url_for('panel_admin.index_admin'))
    return render_template('admin_edit_producto.html', p=p)

@admin_bp.post('/admin/productos/<int:pid>/update')
def editar_producto_guardar(pid:int):
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    p = db.session.get(Producto, pid)
    if not p:
        flash('Producto no encontrado', 'danger'); return redirect(url_for('panel_admin.index_admin'))
    nombre = (request.form.get('nombre') or '').strip()
    categoria = request.form.get('categoria') or None
    detalle = request.form.get('detalle') or None
    stock_minimo = request.form.get('stock_minimo')
    activo_flag = request.form.get('activo')
    if not nombre:
        flash('El nombre es obligatorio', 'danger'); return redirect(url_for('panel_admin.editar_producto_form', pid=pid))
    if nombre != p.nombre and db.session.scalar(db.select(Producto).where(Producto.nombre==nombre)):
        flash('Ya existe otro producto con ese nombre', 'warning'); return redirect(url_for('panel_admin.editar_producto_form', pid=pid))
    p.nombre = nombre; p.categoria = categoria; p.detalle = detalle
    try:
        p.stock_minimo = int(stock_minimo or 0)
    except Exception:
        flash('Stock mínimo inválido', 'danger'); return redirect(url_for('panel_admin.editar_producto_form', pid=pid))
    p.activo = bool(activo_flag)
    db.session.commit()
    flash('Producto actualizado', 'success'); return redirect(url_for('panel_admin.index_admin'))

@admin_bp.post('/admin/productos/<int:pid>/delete')
def eliminar_producto_admin(pid:int):
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    p = db.session.get(Producto, pid)
    if not p:
        flash('Producto no encontrado', 'danger'); return redirect(url_for('panel_admin.index_admin'))
    # Evitar borrar si tiene movimientos
    if (p.entradas and len(p.entradas)>0) or (p.salidas and len(p.salidas)>0):
        flash('No se puede eliminar: el producto tiene movimientos.', 'warning')
        return redirect(url_for('panel_admin.index_admin'))
    db.session.delete(p); db.session.commit()
    flash('Producto eliminado', 'success'); return redirect(url_for('panel_admin.index_admin'))

@admin_bp.post('/admin/stock/entrada')
def admin_entrada():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    producto_id = int(request.form.get('producto_id'))
    cantidad = int(request.form.get('cantidad') or 0)
    obs = request.form.get('observaciones')
    p = db.session.get(Producto, producto_id)
    if not p or cantidad<=0:
        flash('Datos inválidos', 'danger'); return redirect(url_for('panel_admin.index_admin'))
    mov = RegistroEntrada(producto_id=producto_id, cantidad=cantidad, observaciones=obs, usuario_id=session['panel_user_id'])
    p.stock_actual += cantidad
    db.session.add(mov); db.session.commit()
    flash('Entrada registrada', 'success'); return redirect(url_for('panel_admin.index_admin'))

@admin_bp.post('/admin/stock/salida')
def admin_salida():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    producto_id = int(request.form.get('producto_id'))
    cantidad = int(request.form.get('cantidad') or 0)
    obs = request.form.get('observaciones')
    p = db.session.get(Producto, producto_id)
    if not p or cantidad<=0 or p.stock_actual < cantidad:
        flash('Datos inválidos o stock insuficiente', 'danger'); return redirect(url_for('panel_admin.index_admin'))
    mov = RegistroSalida(producto_id=producto_id, cantidad=cantidad, observaciones=obs, usuario_id=session['panel_user_id'])
    p.stock_actual -= cantidad
    db.session.add(mov); db.session.commit()
    flash('Salida registrada', 'success'); return redirect(url_for('panel_admin.index_admin'))



# --- Maquinaria ---
@admin_bp.get('/admin/maquinaria')
def admin_maquinaria():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    return render_template('admin_maquinaria.html')



# --- Trabajadores ---
@admin_bp.get('/admin/trabajadores')
def admin_trabajadores():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    return render_template('admin_trabajadores.html')



# --- Proveedores ---
@admin_bp.get('/admin/proveedores')
def admin_proveedores():
    if not session.get('panel_user_id'):
        return redirect(url_for('panel_admin.login_admin'))
    return render_template('admin_proveedores.html')
