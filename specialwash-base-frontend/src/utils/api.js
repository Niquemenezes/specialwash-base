const BASE_URL = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/$/, "");

async function apiFetch(path, { method = "GET", body, token, headers = {}, withCredentials = false } = {}) {
  const url = `${BASE_URL}${path}`;
  try {
    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
      // Ponlo en true SOLO si tu backend usa cookies y tiene CORS con credentials habilitado:
      credentials: withCredentials ? "include" : "same-origin",
    });

    const contentType = res.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const data = isJson ? await res.json().catch(() => ({})) : await res.text();

    if (!res.ok) {
      const details = typeof data === "string" ? data : JSON.stringify(data);
      throw new Error(`[${res.status} ${res.statusText}] ${url} => ${details}`);
    }
    return data;
  } catch (err) {
    // Error de red / CORS / bloqueo del navegador
    console.error("apiFetch error:", { url, method, body, err });
    throw new Error(`Network/CORS error calling ${url}: ${err.message}`);
  }
}

export const api = {
  login: (payload) => apiFetch("/api/auth/login", { method: "POST", body: payload }),
  adminExists: () => apiFetch("/api/auth/admin-exists"),  // ← debería tener el /auth
  getEmpleados: (token) => apiFetch("/api/auth/usuarios/rol/empleado", { token }),
  getProveedores: (token) => apiFetch("/api/auth/proveedores", { token }),
  crearProducto: (token, payload) => apiFetch("/api/auth/productos", { method: "POST", token, body: payload }),
  registrarEntrada: (token, payload) => apiFetch("/api/auth/registro-entrada", { method: "POST", token, body: payload }),
  registrarSalida: (token, payload) => apiFetch("/api/auth/registro-salida", { method: "POST", token, body: payload }),
};
