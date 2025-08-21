import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowRoles = [] }) {
  const { token, role } = useAuth();
  if (!token) return <Navigate to="/login" replace />;

  const r = (role || "").toLowerCase();
  const normalized = r === "admin" ? "administrador" : r;
  const allowed = new Set([...allowRoles, ...allowRoles.map(x => x === "administrador" ? "admin" : x)]);

  if (allowRoles.length && !allowed.has(r) && !allowed.has(normalized)) {
    return <Navigate to="/" replace />;
  }
  return children;
}
