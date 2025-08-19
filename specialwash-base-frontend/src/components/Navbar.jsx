import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
export default function Navbar() {
  const { token, role, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <div className="brand" onClick={() => navigate(token ? "/admin" : "/")} style={{cursor:"pointer"}}>
        <span className="dot" /><span>SPECIALWASH</span>
      </div>
      <div className="right">
        {!token && (<NavLink to="/login" className={({isActive}) => isActive ? "active" : undefined}>Login</NavLink>)}
        {token && role === "administrador" && (
          <>
            <NavLink to="/admin" className={({isActive}) => isActive ? "active" : undefined}>Panel</NavLink>
            <NavLink to="/admin/empleados" className={({isActive}) => isActive ? "active" : undefined}>Empleados</NavLink>
            <NavLink to="/admin/proveedores" className={({isActive}) => isActive ? "active" : undefined}>Proveedores</NavLink>
            <NavLink to="/admin/productos/nuevo" className={({isActive}) => isActive ? "active" : undefined}>Productos</NavLink>
            <NavLink to="/admin/entradas" className={({isActive}) => isActive ? "active" : undefined}>Entradas</NavLink>
            <NavLink to="/admin/salidas" className={({isActive}) => isActive ? "active" : undefined}>Salidas</NavLink>
          </>
        )}
        {token && (<button onClick={logout}>Salir</button>)}
      </div>
    </nav>
  );
}
