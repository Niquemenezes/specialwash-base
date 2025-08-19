import os
import tempfile
import pytest

from backend.app import create_app
from backend.db import db

@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["JWT_SECRET_KEY"] = "test-jwt"
    os.environ["ADMIN_EMAIL"] = "admin@test.local"
    os.environ["ADMIN_PASSWORD"] = "admin123"

    app = create_app()
    app.testing = True

    with app.app_context():
        db.create_all()

    yield app

    os.close(db_fd)
    os.remove(db_path)

@pytest.fixture()
def client(app):
    return app.test_client()

def test_root_json(client):
    r = client.get("/")
    assert r.status_code == 200
    j = r.get_json()
    assert j["service"] == "specialwash-backend"
    assert j["api"] == "/api"
    assert j["ok"] is True

def test_api_root_json(client):
    r = client.get("/api/")
    assert r.status_code == 200
    j = r.get_json()
    assert j["service"] == "specialwash-backend"
    assert j["api"] == "/api"
    assert j["ok"] is True

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}

def test_seed_admin_and_login(client):
    r = client.get("/api/auth/admin-exists")
    assert r.status_code == 200
    assert r.get_json()["admin_exists"] is False

    r = client.post("/api/auth/seed-admin")
    assert r.status_code == 200
    assert r.get_json()["created"] is True

    r = client.post("/api/auth/seed-admin")
    assert r.status_code == 400

    r = client.post("/api/auth/login", json={"email": "admin@test.local", "password": "admin123"})
    assert r.status_code == 200
    token = r.get_json()["access_token"]
    assert token

    r = client.get("/api/productos", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json() == []

def test_crud_productos_y_stock(client):
    client.post("/api/auth/seed-admin")
    login = client.post("/api/auth/login", json={"email": os.environ["ADMIN_EMAIL"], "password": os.environ["ADMIN_PASSWORD"]})
    token = login.get_json()["access_token"]
    H = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/productos", headers=H, json={"nombre": "Champu", "stock_minimo": 5})
    assert r.status_code == 201
    prod = r.get_json()["producto"]
    pid = prod["id"]
    assert prod["stock_actual"] == 0

    r = client.post("/api/stock/entrada", headers=H, json={"producto_id": pid, "cantidad": 10, "observaciones": "Compra"})
    assert r.status_code == 201
    assert r.get_json()["producto"]["stock_actual"] == 10

    r = client.post("/api/stock/salida", headers=H, json={"producto_id": pid, "cantidad": 3, "observaciones": "Uso"})
    assert r.status_code == 201
    assert r.get_json()["producto"]["stock_actual"] == 7

    r = client.post("/api/stock/salida", headers=H, json={"producto_id": pid, "cantidad": 999})
    assert r.status_code == 400

    r = client.get("/api/stock/entradas", headers=H)
    assert r.status_code == 200
    assert len(r.get_json()) >= 1

    r = client.get("/api/stock/salidas", headers=H)
    assert r.status_code == 200
    assert len(r.get_json()) >= 1
