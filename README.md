# 💰 Cuenta Clara
**Evidencia:** GA8-220501096-AA1-EV01 — SENA  
**Autor:** Carlos Varón  
**Descripción:** Sistema web de gestión de deudas para tenderos de barrio.

---

## 🗂️ Estructura del proyecto

```
cuenta-clara/
├── backend/
│   ├── app.py                    ← Punto de entrada
│   ├── config.py                 ← Configuración
│   ├── database.py               ← Conexión MySQL
│   ├── requirements.txt          ← Dependencias
│   ├── conftest.py               ← Configuración pytest
│   ├── middleware/
│   │   └── auth_middleware.py    ← JWT + SHA-256
│   ├── models/                   ← Capa de datos
│   │   ├── tendero_model.py
│   │   ├── cliente_model.py
│   │   └── deuda_model.py
│   ├── services/                 ← Capa de negocio
│   │   ├── auth_service.py
│   │   ├── cliente_service.py
│   │   ├── deuda_service.py
│   │   └── dashboard_service.py
│   ├── routes/                   ← Capa de presentación
│   │   ├── auth.py
│   │   ├── clientes.py
│   │   ├── deudas.py
│   │   └── dashboard.py
│   └── tests/                   ← Pruebas unitarias
│       ├── test_auth.py
│       ├── test_clientes.py
│       └── test_deudas.py
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── clientes.html
│   ├── deudas.html
│   ├── css/styles.css
│   └── js/api.js
├── database/
│   └── cuenta_clara.sql
└── docs/
    ├── api_documentation.md
    ├── ambiente.md
    ├── casos_de_uso.md
    └── diagramas/
        ├── diagrama_clases.md
        └── diagrama_paquetes_componentes.md
```

---

## 🚀 Instalación

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 🧪 Pruebas

```bash
pytest tests/ -v
# Resultado: 33 passed
```

## 📡 API — 18 endpoints

Ver `docs/api_documentation.md` para documentación completa.

---

## 🏗️ Arquitectura

Patrón Repository + Service Layer:
```
routes/ → services/ → models/ → MySQL
```

*SENA — Servicio Nacional de Aprendizaje · 2024*
