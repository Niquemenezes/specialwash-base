export default function PrivateAdmin() {
  return (
    <div className="grid cols-3">
      <div className="card">
        <h3 className="section-title">Productos</h3>
        <p className="small">Crear productos y definir mínimos de stock.</p>
        <a className="button" href="/admin/productos/nuevo">Abrir</a>
      </div>
      <div className="card">
        <h3 className="section-title">Entradas</h3>
        <p className="small">Registrar entradas (con IVA y descuento).</p>
        <a className="button" href="/admin/entradas">Abrir</a>
      </div>
      <div className="card">
        <h3 className="section-title">Salidas</h3>
        <p className="small">Registrar salidas para control.</p>
        <a className="button" href="/admin/salidas">Abrir</a>
      </div>
    </div>
  );
}
