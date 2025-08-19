import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";
export default function Proveedores() {
  const { token } = useAuth(); const [items, setItems] = useState([]); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  useEffect(()=>{(async()=>{setLoading(true);setError("");try{const data=await api.getProveedores(token);setItems(Array.isArray(data)?data:data?.results||[]);}catch(e){setError(e.message);}finally{setLoading(false);}})();},[token]);
  return (
    <div className="card">
      <h2 className="section-title">Proveedores</h2>
      {loading&&<p className="small">Cargando…</p>}{error&&<p style={{color:"#ff6b6b"}}>{error}</p>}
      <div className="small" style={{overflowX:"auto"}}>
        <table style={{width:"100%",borderCollapse:"collapse"}}>
          <thead><tr><th style={{textAlign:"left",padding:"8px 6px"}}>ID</th><th style={{textAlign:"left",padding:"8px 6px"}}>Nombre</th><th style={{textAlign:"left",padding:"8px 6px"}}>Contacto</th></tr></thead>
          <tbody>{items.map(p=>(
            <tr key={p.id||p._id}><td style={{padding:"8px 6px"}}>{p.id||p._id}</td><td style={{padding:"8px 6px"}}>{p.nombre||p.name}</td><td style={{padding:"8px 6px"}}>{p.contacto||p.email||p.telefono||"-"}</td></tr>
          ))}</tbody>
        </table>
      </div>
    </div>
  );
}
