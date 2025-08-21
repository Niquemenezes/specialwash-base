import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";
const ROLES = ["administrador","empleado","pintor","limpiador","mantenimiento","almacen"];
export default function Login() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  const [rol, setRol] = useState("administrador"); const [adminExiste, setAdminExiste] = useState(true);
  useEffect(() => { api.adminExists().then(() => setAdminExiste(true)).catch(() => setAdminExiste(false)); }, []);
  const handleSubmit = async (e) => { e.preventDefault(); await login({ email, password, rol }); };
  return (
    <div className="card" style={{ maxWidth: 420, margin: "60px auto" }}>
      <h2 className="section-title">Iniciar sesión</h2><p className="small">Acceso al panel interno de SpecialWash</p>
      <form onSubmit={handleSubmit} style={{ display:"grid", gap:12, marginTop:16 }}>
        <label className="label" htmlFor="email">Email</label>
        <input id="email" className="input" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <label className="label" htmlFor="password">Contraseña</label>
        <input id="password" className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        <label className="label" htmlFor="rol">Rol</label>
        <select id="rol" value={rol} onChange={e=>setRol(e.target.value)}>{ROLES.map(r=><option key={r} value={r}>{r}</option>)}</select>
        {error && <div style={{ color:"#ff6b6b" }}>{error}</div>}
        <button className="button" disabled={loading}>{loading ? "Entrando…" : "Entrar"}</button>
      </form>
      {!adminExiste && (<p className="small" style={{ marginTop:12 }}>No existe administrador todavía. Crea uno desde el backend.</p>)}
    </div>
  );
}
