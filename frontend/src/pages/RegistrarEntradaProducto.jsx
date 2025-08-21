import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";
export default function RegistrarEntradaProducto() {
  const { token } = useAuth();
  const [form, setForm] = useState({ producto_id:"", proveedor_id:"", numero_albaran:"", fecha_entrada:new Date().toISOString().slice(0,10), cantidad:0, precio_sin_iva:0, porcentaje_iva:21, descuento:0, observaciones:"" });
  const [msg, setMsg] = useState("");
  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const calcularPrecioConIvaYDescuento = () => { const base=Number(form.precio_sin_iva)||0, iva=Number(form.porcentaje_iva)||0, desc=Number(form.descuento)||0; const conIva=base*(1+iva/100); return (conIva*(1-desc/100)).toFixed(2); };
  const onSubmit = async (e) => { e.preventDefault(); setMsg(""); try { await api.registrarEntrada(token, form); setMsg("Entrada registrada."); } catch(e){ setMsg(e.message);} };
  return (
    <div className="card" style={{ maxWidth: 860 }}>
      <h2 className="section-title">Registrar entrada</h2>
      <form onSubmit={onSubmit} className="grid" style={{ gap: 12 }}>
        <div><label className="label">Producto ID</label><input className="input" name="producto_id" value={form.producto_id} onChange={onChange} required /></div>
        <div><label className="label">Proveedor ID</label><input className="input" name="proveedor_id" value={form.proveedor_id} onChange={onChange} /></div>
        <div><label className="label">Nº albarán / factura</label><input className="input" name="numero_albaran" value={form.numero_albaran} onChange={onChange} /></div>
        <div><label className="label">Fecha de entrada</label><input className="input" type="date" name="fecha_entrada" value={form.fecha_entrada} onChange={onChange} /></div>
        <div><label className="label">Cantidad</label><input className="input" type="number" name="cantidad" value={form.cantidad} onChange={onChange} /></div>
        <div><label className="label">Precio sin IVA</label><input className="input" type="number" step="0.01" name="precio_sin_iva" value={form.precio_sin_iva} onChange={onChange} /></div>
        <div><label className="label">IVA (%)</label><input className="input" type="number" name="porcentaje_iva" value={form.porcentaje_iva} onChange={onChange} /></div>
        <div><label className="label">Descuento (%)</label><input className="input" type="number" name="descuento" value={form.descuento} onChange={onChange} /></div>
        <div><label className="label">Precio final (auto)</label><input className="input" value={calcularPrecioConIvaYDescuento()} readOnly /></div>
        <div><label className="label">Observaciones</label><input className="input" name="observaciones" value={form.observaciones} onChange={onChange} /></div>
        <div><button className="button" type="submit">Guardar</button></div>
      </form>
      {msg && <p className="small" style={{ marginTop: 10 }}>{msg}</p>}
    </div>
  );
}
