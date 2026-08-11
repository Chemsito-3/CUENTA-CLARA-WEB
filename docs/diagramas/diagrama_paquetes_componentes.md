# Diagramas de Paquetes y Componentes
## Evidencia GA8-220501096-AA1-EV01 — SENA
**Autor:** Carlos Varón | **Proyecto:** Cuenta Clara

---

# 1. Diagrama de Paquetes

Muestra cómo está organizado el código en paquetes y las dependencias entre ellos.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CUENTA CLARA - SISTEMA                        │
│                                                                   │
│  ┌─────────────────┐         ┌──────────────────────────────┐   │
│  │   <<paquete>>   │         │       <<paquete>>             │   │
│  │    frontend/    │         │         backend/              │   │
│  │                 │  HTTP   │                               │   │
│  │  index.html     │◄───────►│  ┌─────────────────────┐    │   │
│  │  dashboard.html │  JSON   │  │   <<paquete>>        │    │   │
│  │  clientes.html  │         │  │      routes/         │    │   │
│  │  deudas.html    │         │  │                      │    │   │
│  │  css/           │         │  │  auth.py             │    │   │
│  │  js/api.js      │         │  │  clientes.py         │    │   │
│  └─────────────────┘         │  │  deudas.py           │    │   │
│                               │  │  dashboard.py        │    │   │
│                               │  └──────────┬───────────┘    │   │
│                               │             │ usa             │   │
│                               │  ┌──────────▼───────────┐    │   │
│                               │  │   <<paquete>>        │    │   │
│                               │  │     services/        │    │   │
│                               │  │                      │    │   │
│                               │  │  auth_service.py     │    │   │
│                               │  │  cliente_service.py  │    │   │
│                               │  │  deuda_service.py    │    │   │
│                               │  │  dashboard_service.py│    │   │
│                               │  └──────────┬───────────┘    │   │
│                               │             │ usa             │   │
│                               │  ┌──────────▼───────────┐    │   │
│                               │  │   <<paquete>>        │    │   │
│                               │  │      models/         │    │   │
│                               │  │                      │    │   │
│                               │  │  tendero_model.py    │    │   │
│                               │  │  cliente_model.py    │    │   │
│                               │  │  deuda_model.py      │    │   │
│                               │  └──────────┬───────────┘    │   │
│                               │             │ usa             │   │
│                               │  ┌──────────▼───────────┐    │   │
│                               │  │   <<paquete>>        │    │   │
│                               │  │    middleware/       │    │   │
│                               │  │  auth_middleware.py  │    │   │
│                               │  └──────────────────────┘    │   │
│                               │                               │   │
│                               └──────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────┐         ┌──────────────────────────────┐   │
│  │   <<paquete>>   │         │       <<paquete>>             │   │
│  │   database/     │         │         tests/               │   │
│  │                 │         │                               │   │
│  │  cuenta_clara   │         │  test_auth.py                │   │
│  │  .sql           │         │  test_clientes.py            │   │
│  └─────────────────┘         │  test_deudas.py              │   │
│                               └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Dependencias entre paquetes

```
routes/ ──────────► services/ ──────────► models/ ──────────► MySQL
   │                    │                    │
   │                    │                    └──────────────► database.py
   │                    │
   └────────────────► middleware/
```

**Regla de dependencia:** Las dependencias van en una sola dirección — de arriba hacia abajo. Las rutas nunca acceden directamente a los modelos, siempre pasan por los servicios.

---

# 2. Diagrama de Componentes

Muestra los componentes del sistema y cómo se comunican entre sí.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Navegador)                           │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Interfaz Web (HTML/JS)                        │  │
│  │                                                                  │  │
│  │  ┌───────────┐  ┌─────────────┐  ┌───────────┐  ┌──────────┐  │  │
│  │  │ index.html│  │dashboard.html│  │clientes   │  │deudas    │  │  │
│  │  │ (Login)   │  │(Panel)      │  │.html      │  │.html     │  │  │
│  │  └─────┬─────┘  └──────┬──────┘  └─────┬─────┘  └────┬─────┘  │  │
│  │        └───────────────┴────────────────┴─────────────┘         │  │
│  │                              │                                   │  │
│  │                    ┌─────────▼──────────┐                        │  │
│  │                    │     js/api.js       │                        │  │
│  │                    │  (Fetch API / JWT)  │                        │  │
│  │                    └─────────┬──────────┘                        │  │
│  └──────────────────────────────┼──────────────────────────────────┘  │
└─────────────────────────────────┼────────────────────────────────────┘
                                  │ HTTP/JSON
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      SERVIDOR (Python Flask)                           │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    app.py (Punto de entrada)                     │  │
│  │              Flask + CORS + Blueprints registrados               │  │
│  └──────────────────────────┬─────────────────────────────────────┘  │
│                              │                                         │
│  ┌───────────────────────────▼────────────────────────────────────┐  │
│  │                   Capa de Rutas (routes/)                        │  │
│  │                                                                  │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────┐  │  │
│  │  │  auth.py │  │  clientes.py │  │deudas.py │  │dashboard  │  │  │
│  │  │/api/auth │  │/api/clientes │  │/api/deuda│  │.py        │  │  │
│  │  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └─────┬─────┘  │  │
│  └───────┼───────────────┼───────────────┼───────────────┼─────────┘  │
│          └───────────────┴───────────────┴───────────────┘            │
│                                  │                                     │
│  ┌───────────────────────────────▼────────────────────────────────┐  │
│  │                  Capa de Servicios (services/)                   │  │
│  │                                                                  │  │
│  │  ┌─────────────┐  ┌────────────────┐  ┌───────────────────┐    │  │
│  │  │auth_service │  │cliente_service │  │deuda_service      │    │  │
│  │  │             │  │                │  │dashboard_service  │    │  │
│  │  └──────┬──────┘  └───────┬────────┘  └─────────┬─────────┘    │  │
│  └─────────┼─────────────────┼──────────────────────┼──────────────┘  │
│            └─────────────────┴──────────────────────┘                 │
│                                  │                                     │
│  ┌───────────────────────────────▼────────────────────────────────┐  │
│  │                   Capa de Modelos (models/)                      │  │
│  │                                                                  │  │
│  │  ┌───────────────┐  ┌────────────────┐  ┌─────────────────┐    │  │
│  │  │tendero_model  │  │ cliente_model  │  │  deuda_model    │    │  │
│  │  └───────┬───────┘  └───────┬────────┘  └────────┬────────┘    │  │
│  └──────────┼─────────────────┼────────────────────┼──────────────┘  │
│             └─────────────────┴────────────────────┘                  │
│                                  │                                     │
│  ┌───────────────────────────────▼────────────────────────────────┐  │
│  │              Componente de Seguridad (middleware/)               │  │
│  │                   auth_middleware.py                             │  │
│  │            SHA-256 + JWT Token + Decorador @token_required      │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ MySQL Connector
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      BASE DE DATOS (MySQL)                             │
│                                                                        │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌────────────┐  │
│   │ tenderos  │    │ clientes  │    │  deudas   │    │detalle_    │  │
│   │           │1──N│           │1──N│           │1──N│deuda       │  │
│   └───────────┘    └───────────┘    └───────────┘    └────────────┘  │
│                                                                        │
│              TRIGGERS: actualizar_total, verificar_vencimiento         │
└──────────────────────────────────────────────────────────────────────┘
```

---

# 3. Mapa de Navegación

```
                    ┌─────────────────┐
                    │   index.html    │
                    │  (Login/Registro)│
                    └────────┬────────┘
                             │ autenticación exitosa
                             ▼
                    ┌─────────────────┐
              ┌────►│ dashboard.html  │◄────┐
              │     │ (Panel principal)│     │
              │     └────────┬────────┘     │
              │              │               │
              │    ┌─────────┴──────────┐    │
              │    ▼                    ▼    │
              │  ┌──────────────┐  ┌──────────────┐
              │  │clientes.html │  │ deudas.html  │
              │  │(Gestión de   │  │(Gestión de   │
              │  │ clientes)    │  │ deudas)      │
              │  └──────┬───────┘  └──────┬───────┘
              │         │                  │
              └─────────┴──────────────────┘
                         navegación libre
```
