const BASE = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/+$/, "");
function authHeaders(extra = {}) {
  const token = sessionStorage.getItem("token");
  return { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...extra };
}
export async function apiGet(path){ const r=await fetch(`${BASE}${path}`,{headers:authHeaders()}); if(!r.ok) throw new Error(`${r.status} ${r.statusText}`); return r.json(); }
export async function apiPost(path,body){ const r=await fetch(`${BASE}${path}`,{method:"POST",headers:authHeaders(),body:JSON.stringify(body)}); const t=await r.text(); if(!r.ok) throw new Error(t||`${r.status} ${r.statusText}`); try{return JSON.parse(t);}catch{return t;} }
