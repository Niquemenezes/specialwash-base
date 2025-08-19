
from flask import redirect, url_for, session, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from .db import db
from .models import User, Producto, RegistroEntrada, RegistroSalida

# Index protegido + endpoint propio
class SecureAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get('panel_user_id'):
            return redirect(url_for('panel_admin.login_admin', next=request.url))
        return super().index()

    def is_accessible(self):
        return bool(session.get('panel_user_id'))

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('panel_admin.login_admin', next=request.url))

# Base protegida para vistas de modelos
class SecureModelView(ModelView):
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_display_pk = True

    def is_accessible(self):
        return bool(session.get('panel_user_id'))

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('panel_admin.login_admin', next=request.url))

# Personalizaciones ejemplo
class ProductoAdmin(SecureModelView):
    column_searchable_list = ('nombre', 'categoria',)
    column_filters = ('activo', 'categoria',)
    column_list = ('id', 'nombre', 'categoria', 'stock_actual', 'stock_minimo', 'activo')
    form_columns = ('nombre', 'categoria', 'detalle', 'stock_minimo', 'activo')

class UserAdmin(SecureModelView):
    column_list = ('id', 'email', 'role', 'created_at')
    column_searchable_list = ('email',)
    form_columns = ('email', 'role')

def setup_superadmin(app):
    # endpoint='superadmin' y url base '/superadmin'
    admin = Admin(
        app,
        name='SpecialWash Superadmin',
        index_view=SecureAdminIndex(name='Inicio', url='/superadmin', endpoint='superadmin'),
        template_mode='bootstrap3',
        endpoint='superadmin'
    )

    # Registra modelos con endpoints únicos
    admin.add_view(UserAdmin(User, db.session, category='Core', endpoint='superadmin_users'))
    admin.add_view(ProductoAdmin(Producto, db.session, category='Inventario', endpoint='superadmin_productos'))
    admin.add_view(SecureModelView(RegistroEntrada, db.session, category='Inventario', endpoint='superadmin_entradas'))
    admin.add_view(SecureModelView(RegistroSalida, db.session, category='Inventario', endpoint='superadmin_salidas'))
