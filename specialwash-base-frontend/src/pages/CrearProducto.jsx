import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";
export default function CrearProducto() {
  const { token } = useAuth();
  const [form, setForm] = useState({ nombre:"", detalle:"", categoria:"lavado", stock_minimo:0, proveedor_id:"" });
  const [msg, setMsg] = useState("");
  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const onSubmit = async (e) => { e.preventDefault(); setMsg(""); try { await api.crearProducto(token, form); setMsg("Producto creado correctamente."); setForm({ nombre:"", detalle:"", categoria:"lavado", stock_minimo:0, proveedor_id:"" }); } catch (e) { setMsg(e.message); } };
  return (
    <div className="card" style={{ maxWidth: 720 }}>
      <h2 className="section-title">Crear producto</h2>
      <form onSubmit={onSubmit} className="grid" style={{ gap: 12 }}>
        <div><label className="label">Nombre</label><input className="input" name="nombre" value={form.nombre} onChange={onChange} required /></div>
        <div><label className="label">Detalle</label><input className="input" name="detalle" value={form.detalle} onChange={onChange} /></div>
        <div><label className="label">Categoría</label><select className="input" name="categoria" value={form.categoria} onChange={onChange}><option value="lavado">Lavado</option><option value="pintura">Pintura</option></select></div>
        <div><label className="label">Stock mínimo</label><input className="input" type="number" name="stock_minimo" value={form.stock_minimo} onChange={onChange} /></div>
        <div><label className="label">Proveedor ID (opcional)</label><input className="input" name="proveedor_id" value={form.proveedor_id} onChange={onChange} /></div>
        <div><button className="button" type="submit">Guardar</button></div>
      </form>
      {msg && <p className="small" style={{ marginTop: 10 }}>{msg}</p>}
    </div>
  );
}
