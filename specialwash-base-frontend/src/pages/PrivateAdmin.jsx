export default function PrivateAdmin() {
  return (
    <div className="grid cols-3">
      <div className="card"><h3 className="section-title">Empleados</h3><p className="small">Alta, edición y listado de empleados.</p><a className="button" href="/admin/empleados">Abrir</a></div>
      <div className="card"><h3 className="section-title">Proveedores</h3><p className="small">Gestión de proveedores y contactos.</p><a className="button" href="/admin/proveedores">Abrir</a></div>
      <div className="card"><h3 className="section-title">Productos</h3><p className="small">Crear productos y definir mínimos de stock.</p><a className="button" href="/admin/productos/nuevo">Abrir</a></div>
      <div className="card"><h3 className="section-title">Entradas</h3><p className="small">Registrar entradas (IVA/Dto.).</p><a className="button" href="/admin/entradas">Abrir</a></div>
      <div className="card"><h3 className="section-title">Salidas</h3><p className="small">Registrar salidas para control.</p><a className="button" href="/admin/salidas">Abrir</a></div>
    </div>
  );
}
