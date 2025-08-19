import React, { createContext, useContext, useEffect, useMemo, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../utils/api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => sessionStorage.getItem("token") || "");
  const [role, setRole] = useState(() => sessionStorage.getItem("role") || "");
  const [user, setUser] = useState(() => {
    const raw = sessionStorage.getItem("user");
    try { return raw ? JSON.parse(raw) : null; } catch { return null; }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    token ? sessionStorage.setItem("token", token) : sessionStorage.removeItem("token");
    role ? sessionStorage.setItem("role", role) : sessionStorage.removeItem("role");
    user ? sessionStorage.setItem("user", JSON.stringify(user)) : sessionStorage.removeItem("user");
  }, [token, role, user]);

  const login = useCallback(async ({ email, password, rol }) => {
    setLoading(true); setError("");
    try {
      const data = await api.login({ email, password });
      const jwt = data?.access_token || data?.token || "";
      const payload = data?.user || data?.usuario || null;
      const normalizedRole = (payload?.rol || payload?.role || rol || "").toString().toLowerCase();

      setToken(jwt);
      setUser(payload);
      setRole(normalizedRole);

      if (normalizedRole === "administrador") navigate("/admin", { replace: true });
      else navigate("/", { replace: true });
    } catch (e) {
      setError(e.message || "Error de login");
      throw e;
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const logout = useCallback(() => {
    setToken(""); setUser(null); setRole("");
    navigate("/login", { replace: true });
  }, [navigate]);

  const value = useMemo(
    () => ({ token, user, role, login, logout, loading, error }),
    [token, user, role, login, logout, loading, error]
  );

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export const useAuth = () => useContext(AuthCtx);
