#!/usr/bin/env bash
set -e

# ==== Detectar URLs reales de Codespaces ====
FRONT_URL=$(gp url 3000)
BACK_URL=$(gp url 3001)
echo "🌐 FRONT_URL = $FRONT_URL"
echo "🌐 BACK_URL  = $BACK_URL"

# ==== Liberar puertos y procesos colgados ====
lsof -t -i :3000 -i :3001 2>/dev/null | xargs -r kill || true
pkill -f "flask run" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "gunicorn .* backend.app:app" 2>/dev/null || true

# ==== Backend ====
python -m venv .venv >/dev/null 2>&1 || true
source .venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=backend/app.py
export PORT=3001
export CORS_ORIGINS="$FRONT_URL"
export DATABASE_URL=sqlite:///local.db

# Migraciones (no rompas si aún no hay)
flask db upgrade || true

# Arrancar backend en background
(flask run --host 0.0.0.0 --port $PORT &) 
BACK_PID=$!
sleep 2
echo "🚀 Backend en $BACK_URL"

# ==== Frontend ====
cd specialwash-base-frontend
# apuntar front al backend de Codespaces (HTTPS)
echo "REACT_APP_BACKEND_URL=$BACK_URL" > .env
npm install
echo "🌐 .env escrito con REACT_APP_BACKEND_URL=$BACK_URL"
echo "🚀 Front en $FRONT_URL"
npm start

# Al cerrar el front, matar backend
kill $BACK_PID 2>/dev/null || true
