import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";
export default function RegistrarSalidaProducto() {
  const { token } = useAuth();
  const [form, setForm] = useState({ producto_id:"", cantidad:0, fecha_salida:new Date().toISOString().slice(0,10), observaciones:"" });
  const [msg, setMsg] = useState("");
  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const onSubmit = async (e) => { e.preventDefault(); setMsg(""); try { await api.registrarSalida(token, form); setMsg("Salida registrada."); } catch (e) { setMsg(e.message); } };
  return (
    <div className="card" style={{ maxWidth: 720 }}>
      <h2 className="section-title">Registrar salida</h2>
      <form onSubmit={onSubmit} className="grid" style={{ gap: 12 }}>
        <div><label className="label">Producto ID</label><input className="input" name="producto_id" value={form.producto_id} onChange={onChange} required /></div>
        <div><label className="label">Fecha</label><input className="input" type="date" name="fecha_salida" value={form.fecha_salida} onChange={onChange} /></div>
        <div><label className="label">Cantidad</label><input className="input" type="number" name="cantidad" value={form.cantidad} onChange={onChange} /></div>
        <div><label className="label">Observaciones</label><input className="input" name="observaciones" value={form.observaciones} onChange={onChange} /></div>
        <div><button className="button" type="submit">Guardar</button></div>
      </form>
      {msg && <p className="small" style={{ marginTop: 10 }}>{msg}</p>}
    </div>
  );
}
