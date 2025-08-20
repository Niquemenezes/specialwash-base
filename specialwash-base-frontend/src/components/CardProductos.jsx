import React, { useEffect, useMemo, useState } from "react";
import { apiGet, apiPost } from "../services/api";

const normaliza = (p) => {
  const stockActual = p.stock_actual ?? p.stock ?? p.cantidad ?? p.cantidad_total ?? 0;
  const stockMinimo = p.stock_minimo ?? p.min_stock ?? p.stockMinimo ?? p.minimo ?? 0;
  const nombre = p.nombre ?? p.nombre_producto ?? p.name ?? p.detalle ?? "—";
  const categoria = p.categoria ?? p.category ?? "—";
  const proveedor = p.proveedor?.nombre ?? p.proveedor_nombre ?? p.proveedor ?? "—";
  return {
    id: p.id ?? p.producto_id ?? nombre,
    nombre, categoria, proveedor,
    stockActual: Number(stockActual) || 0,
    stockMinimo: Number(stockMinimo) || 0,
  };
};

export default function CardProductos() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [filter, setFilter] = useState("");

  // Form
  const [nombre, setNombre] = useState("");
  const [detalle, setDetalle] = useState("");
  const [categoria, setCategoria] = useState("");
  const [proveedor, setProveedor] = useState("");
  const [stockMinimo, setStockMinimo] = useState(0);
  const [stockInicial, setStockInicial] = useState(0); // opcional

  async function cargar() {
    try {
      setErr(""); setLoading(true);
      const data = await apiGet("/api/productos");
      const list = Array.isArray(data) ? data : data?.results || data?.items || [];
      setProductos(list.map(normaliza));
    } catch (e) {
      console.error(e); setErr("No se pudieron cargar los productos.");
    } finally { setLoading(false); }
  }
  useEffect(() => { cargar(); }, []);

  async function onCrear(e) {
    e.preventDefault(); setErr("");
    try {
      const nuevo = await apiPost("/api/productos", {
        nombre, detalle, categoria, proveedor,
        stock_minimo: Number(stockMinimo) || 0,
      });

      if ((Number(stockInicial) || 0) > 0) {
        try {
          await apiPost("/api/registro-entrada", {
            producto_id: nuevo.id ?? nuevo.producto_id,
            cantidad: Number(stockInicial),
            proveedor: proveedor || "Stock inicial",
            numero_albaran: "INIT",
            fecha_entrada: new Date().toISOString().slice(0, 10),
            precio_sin_iva: 0,
            porcentaje_iva: 0,
            descuento: 0,
            observaciones: "Carga inicial desde frontend",
          });
        } catch (e) { console.warn("Entrada inicial opcional falló:", e); }
      }

      setNombre(""); setDetalle(""); setCategoria("");
      setProveedor(""); setStockMinimo(0); setStockInicial(0);
      await cargar();
    } catch (e) {
      console.error(e); setErr(e.message || "Error al crear el producto.");
    }
  }

  const productosFiltrados = useMemo(() => {
    const q = filter.trim().toLowerCase();
    if (!q) return productos;
    return productos.filter(p =>
      [p.nombre, p.categoria, p.proveedor].join(" ").toLowerCase().includes(q)
    );
  }, [filter, productos]);

  return (
    <div className="card shadow-sm mb-4">
      <div className="card-header d-flex align-items-center justify-content-between">
        <h5 className="mb-0">Productos</h5>
        <input
          className="form-control form-control-sm"
          style={{ maxWidth: 300 }}
          placeholder="Buscar (nombre, categoría, proveedor)"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>

      <div className="card-body">
        <form onSubmit={onCrear} className="row g-3 mb-4">
          <div className="col-md-4">
            <label className="form-label">Nombre *</label>
            <input className="form-control" required value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Ej: APC Flowey 10L" />
          </div>
          <div className="col-md-4">
            <label className="form-label">Categoría</label>
            <input className="form-control" value={categoria}
              onChange={(e) => setCategoria(e.target.value)}
              placeholder="Lavado / Pintura / Útiles…" />
          </div>
          <div className="col-md-4">
            <label className="form-label">Proveedor</label>
            <input className="form-control" value={proveedor}
              onChange={(e) => setProveedor(e.target.value)}
              placeholder="Flowey / Otro" />
          </div>
          <div className="col-md-8">
            <label className="form-label">Detalle</label>
            <input className="form-control" value={detalle}
              onChange={(e) => setDetalle(e.target.value)}
              placeholder="Descripción breve del producto" />
          </div>
          <div className="col-md-2">
            <label className="form-label">Stock mínimo</label>
            <input type="number" min="0" className="form-control" value={stockMinimo}
              onChange={(e) => setStockMinimo(e.target.value)} />
          </div>
          <div className="col-md-2">
            <label className="form-label">Stock inicial (opcional)</label>
            <input type="number" min="0" className="form-control" value={stockInicial}
              onChange={(e) => setStockInicial(e.target.value)} />
          </div>
          <div className="col-12 d-flex gap-2">
            <button className="btn btn-dark" type="submit">Crear producto</button>
            {err && <div className="text-danger align-self-center">{err}</div>}
          </div>
        </form>

        {loading ? (<div>Cargando…</div>) : (
          <div className="table-responsive">
            <table className="table table-sm align-middle">
              <thead>
                <tr>
                  <th>Producto</th><th>Categoría</th><th>Proveedor</th>
                  <th className="text-end">Stock</th>
                  <th className="text-end">Mínimo</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {productosFiltrados.map((p) => {
                  const bajo = p.stockActual <= p.stockMinimo;
                  return (
                    <tr key={p.id}>
                      <td>{p.nombre}</td>
                      <td>{p.categoria}</td>
                      <td>{p.proveedor}</td>
                      <td className="text-end">{p.stockActual}</td>
                      <td className="text-end">{p.stockMinimo}</td>
                      <td>{bajo
                        ? <span className="badge text-bg-danger">Bajo stock</span>
                        : <span className="badge text-bg-success">OK</span>}
                      </td>
                    </tr>
                  );
                })}
                {productosFiltrados.length === 0 && (
                  <tr><td colSpan="6" className="text-center text-muted py-4">
                    No hay productos que coincidan con la búsqueda.
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
