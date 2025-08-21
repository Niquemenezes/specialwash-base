from flask import Blueprint, request, redirect

compat_bp = Blueprint("compat", __name__)

@compat_bp.before_app_request
def compat_redirect():
    p = request.path or ""
    if p.startswith("/api/"):
        return  # ya correcto
    # Acepta /auth, /productos y /stock sin prefijo y redirige con 307
    if p.startswith(("/auth", "/productos", "/stock")):
        qs = ("?" + request.query_string.decode()) if request.query_string else ""
        return redirect("/api" + p + qs, code=307)
