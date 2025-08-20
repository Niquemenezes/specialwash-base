# SpecialWash App

Sistema de gestión interna para el centro de estética de coches **SpecialWash**, desarrollado con **Flask** (backend) y **React** (frontend).

## 🚀 Tecnologías principales

- Backend: Flask, Flask-JWT-Extended, SQLAlchemy, Flask-Migrate, Flask-CORS, Gunicorn
- Frontend: React (Create React App)
- Base de datos: PostgreSQL (Render)
- Despliegue: [Render.com](https://render.com)

---

## 📁 Estructura del proyecto

```
specialwash-base/
│
├── backend/                # Aplicación Flask
│   ├── app.py              # App principal
│   ├── db/                 # Modelos y migraciones
│   └── routes/             # Rutas de API
│
├── specialwash-base-frontend/    # Aplicación React
│   ├── public/
│   └── src/
│
├── requirements.txt
├── render.yaml
└── .env.example            # Variables de entorno (plantilla)
```

---

## ⚙️ Configuración local (desarrollo)

1. Clona el repositorio:

```bash
git clone https://github.com/Niquemenezes/specialwash-base.git
cd specialwash-base
```

2. Crea y activa un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Crea el archivo `.env` basado en `.env.example` y añade tus valores.

5. Aplica las migraciones (si aún no existen):

```bash
flask db init
flask db migrate
flask db upgrade
```

6. Levanta el backend:

```bash
python backend/app.py
```

7. En otra terminal, instala dependencias del frontend y ejecuta:

```bash
cd specialwash-base-frontend
npm install
npm start
```

Accede a `http://localhost:3000` para ver la app funcionando.

---

## ☁️ Despliegue en Render

El archivo `render.yaml` permite desplegar automáticamente:

- 🐍 Backend Flask
- ⚛️ Frontend React (estático)
- 🐘 Base de datos PostgreSQL

### Pasos:

1. Sube el proyecto a GitHub.
2. Entra a [render.com](https://dashboard.render.com/blueprint).
3. Elige **"Deploy a Blueprint"**.
4. Pega el link de tu repo y confirma.
5. Render detectará automáticamente:
   - La base de datos
   - El backend (Flask)
   - El frontend (React)

✅ Se configuran automáticamente las variables `DATABASE_URL`, `REACT_APP_BACKEND_URL`, `CORS_ORIGINS`, `SECRET_KEY`, etc.

---

## 🔐 Variables necesarias (.env)

Revisa el archivo `.env.example` para ver todas las variables necesarias en tu entorno local.

---

## 👤 Autora

Monique de Menezes — [SpecialWash](https://specialwash.es)