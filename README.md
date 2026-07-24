# 💰 Cuenta Clara
**Evidencia:** GA7-220501096-AA5-EV03 — SENA  
**Autor:** Carlos Varón  
**Descripción:** Sistema web de gestión de deudas para tenderos de barrio.  
Permite registrar clientes, deudas con productos fiados, pagos y alertas de vencimiento.

---

## 🗂️ Estructura del proyecto

```
cuenta-clara/
├── backend/
│   ├── app.py                  ← Punto de entrada del servidor
│   ├── config.py               ← Configuración (BD, JWT)
│   ├── database.py             ← Utilidad de conexión MySQL
│   ├── requirements.txt        ← Dependencias Python
│   ├── middleware/
│   │   └── auth_middleware.py  ← Autenticación JWT
│   └── routes/
│       ├── auth.py             ← Endpoints de autenticación
│       ├── clientes.py         ← CRUD de clientes
│       ├── deudas.py           ← Gestión de deudas y pagos
│       └── dashboard.py        ← Resumen y alertas
├── frontend/
│   ├── index.html              ← Login y registro
│   ├── dashboard.html          ← Panel principal
│   ├── clientes.html           ← Gestión de clientes
│   ├── deudas.html             ← Gestión de deudas
│   ├── css/styles.css          ← Estilos globales
│   └── js/api.js               ← Utilidades de la API
├── database/
│   └── cuenta_clara.sql        ← Script de base de datos
├── docs/
│   └── api_documentation.md   ← Documentación de los 18 endpoints
└── README.md
```

---

## ⚙️ Requisitos previos

- Python 3.8 o superior
- MySQL 8.0 o superior
- MySQL Workbench (recomendado)
- Postman (para pruebas)

---

## 🚀 Instalación y configuración

### Paso 1 — Base de datos

1. Abre MySQL Workbench y conéctate al servidor
2. Ve a `File → Open SQL Script`
3. Abre el archivo `database/cuenta_clara.sql`
4. Ejecuta con el botón ⚡
5. Verifica que aparezca la base de datos `cuenta_clara`

### Paso 2 — Configurar credenciales

Abre `backend/config.py` y edita:

```python
DB_PASSWORD = 'tu_contraseña_mysql'
DB_PORT     = 3306   # o 3307 según tu instalación
```

### Paso 3 — Entorno virtual e instalación

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Paso 4 — Ejecutar el servidor

```bash
python app.py
```

El servidor arranca en: **http://localhost:5000**

### Paso 5 — Abrir el frontend

Abre en el navegador:
```
frontend/index.html
```

---

## 🧪 Credenciales de prueba

| Email | Contraseña | Tienda |
|-------|-----------|--------|
| carlos@tienda.com | tienda123 | Tienda Don Carlos |

---

## 📡 Endpoints disponibles (18 en total)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/auth/registro | Registrar tendero |
| POST | /api/auth/login | Iniciar sesión |
| GET | /api/auth/perfil | Ver perfil |
| GET | /api/clientes/ | Listar clientes |
| POST | /api/clientes/ | Crear cliente |
| GET | /api/clientes/{id} | Ver cliente |
| PUT | /api/clientes/{id} | Actualizar cliente |
| DELETE | /api/clientes/{id} | Eliminar cliente |
| GET | /api/deudas/ | Listar deudas |
| POST | /api/deudas/ | Crear deuda |
| GET | /api/deudas/{id} | Ver deuda |
| POST | /api/deudas/{id}/productos | Agregar producto |
| PATCH | /api/deudas/{id}/pagar | Registrar pago |
| DELETE | /api/deudas/{id} | Eliminar deuda |
| GET | /api/dashboard/resumen | Resumen general |
| GET | /api/dashboard/alertas | Alertas vencimiento |
| GET | /api/dashboard/top-deudores | Top deudores |
| GET | /health | Estado del servidor |

Ver documentación completa en `docs/api_documentation.md`

---

## 🗂️ Control de versiones — Git y GitHub

```bash
# Inicializar repositorio
git init
git add .
git commit -m "feat: Cuenta Clara API REST - GA7-220501096-AA5-EV03"

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/cuenta-clara.git
git branch -M main
git push -u origin main
```

---

## 🔒 Seguridad implementada

- Contraseñas cifradas con **SHA-256**
- Autenticación con **JWT** (tokens de 24h)
- Cada tendero solo accede a **sus propios datos**
- Eliminación lógica de clientes (no borra historial)
- Deudas pagadas no se pueden eliminar

---

*SENA — Servicio Nacional de Aprendizaje · 2024*
