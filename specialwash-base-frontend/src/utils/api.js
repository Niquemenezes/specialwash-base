const BASE_URL = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/$/, "");

async function apiFetch(path, { method = "GET", body, token, headers = {} } = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const ct = res.headers.get("content-type") || "";
  const isJson = ct.includes("application/json");
  const data = isJson ? await res.json().catch(() => ({})) : await res.text();

  if (!res.ok) {
    const details = typeof data === "string" ? data : JSON.stringify(data);
    throw new Error(`[${res.status} ${res.statusText}] ${url} => ${details}`);
  }
  return data;
}

export const api = {
  // Auth
  login: (payload) => apiFetch("/api/auth/login", { method: "POST", body: payload }),
  adminExists: () => apiFetch("/api/auth/admin-exists"),

  // Productos (coincide con backend/routes.py)
  crearProducto: (token, payload) => apiFetch("/api/productos", { method: "POST", token, body: payload }),

  // Stock (coincide con backend/routes.py)
  registrarEntrada: (token, payload) => apiFetch("/api/stock/entrada", { method: "POST", token, body: payload }),
  registrarSalida: (token, payload) => apiFetch("/api/stock/salida", { method: "POST", token, body: payload }),

  // TODO: endpoints aún no implementados en el backend (deja placeholder)
  getEmpleados: async () => { return []; },
  getProveedores: async () => { return []; },
};
