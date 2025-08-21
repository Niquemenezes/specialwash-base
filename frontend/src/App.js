import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import PrivateAdmin from "./pages/PrivateAdmin";
import Empleados from "./pages/Empleados";
import Proveedores from "./pages/Proveedores";
import CrearProducto from "./pages/CrearProducto";
import RegistrarEntradaProducto from "./pages/RegistrarEntradaProducto";
import RegistrarSalidaProducto from "./pages/RegistrarSalidaProducto";
import ProtectedRoute from "./routes/ProtectedRoute";

export default function App() {
  return (
    <AuthProvider>
      <div className="app-shell">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowRoles={["administrador"]}>
                  <PrivateAdmin />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/empleados"
              element={
                <ProtectedRoute allowRoles={["administrador"]}>
                  <Empleados />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/proveedores"
              element={
                <ProtectedRoute allowRoles={["administrador"]}>
                  <Proveedores />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/productos/nuevo"
              element={
                <ProtectedRoute allowRoles={["administrador"]}>
                  <CrearProducto />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/entradas"
              element={
                <ProtectedRoute allowRoles={["administrador"]}>
                  <RegistrarEntradaProducto />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/salidas"
              element={
                <ProtectedRoute allowRoles={["administrador"]}>
                  <RegistrarSalidaProducto />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<h2>404 — Página no encontrada</h2>} />
          </Routes>
        </div>
      </div>
    </AuthProvider>
  );
}
