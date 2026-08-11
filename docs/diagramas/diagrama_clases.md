---
title: Diagrama de Clases — Cuenta Clara
---

# Diagrama de Clases
## Evidencia GA8-220501096-AA1-EV01 — SENA
**Autor:** Carlos Varón | **Proyecto:** Cuenta Clara

---

## Descripción

El diagrama de clases muestra las entidades del sistema, sus atributos, métodos y las relaciones entre ellas. Cuenta Clara sigue el **patrón Repository** con tres capas:

- **Models** → acceso a datos (repositorios)
- **Services** → lógica de negocio
- **Routes** → controladores HTTP

---

## Diagrama

```mermaid
classDiagram

    %% ── MODELOS (Capa de acceso a datos) ──────────────────────────────────
    class TenderoModel {
        +crear(nombre, email, hash, tienda, tel) int
        +buscar_por_email(email) dict
        +buscar_por_credenciales(email, hash) dict
        +buscar_por_id(tendero_id) dict
    }

    class ClienteModel {
        +listar(tendero_id, buscar) list
        +buscar_por_id(cliente_id, tendero_id) dict
        +buscar_por_nombre(nombre, tendero_id) dict
        +crear(tendero_id, nombre, tel, dir) int
        +actualizar(id, tendero_id, campos, vals) int
        +eliminar(cliente_id, tendero_id) int
        +contar_deudas_activas(cliente_id) int
        +obtener_resumen_deudas(cliente_id) dict
    }

    class DeudaModel {
        +listar(tendero_id, estado, cliente_id) list
        +buscar_por_id(deuda_id, tendero_id) dict
        +crear(cliente_id, tendero_id, fecha, obs) int
        +agregar_producto(deuda_id, nombre, precio, cant, sub) int
        +obtener_productos(deuda_id) list
        +marcar_pagada(deuda_id, tendero_id) int
        +eliminar(deuda_id, tendero_id) int
        +obtener_resumen(tendero_id) dict
        +obtener_vencidas(tendero_id) list
        +obtener_proximas(tendero_id, dias) list
        +obtener_top_deudores(tendero_id, limite) list
    }

    %% ── SERVICIOS (Capa de lógica de negocio) ─────────────────────────────
    class AuthService {
        +registrar(nombre, email, clave, tienda, tel) dict
        +login(email, clave) dict
        +obtener_perfil(tendero_id) dict
    }

    class ClienteService {
        +listar(tendero_id, buscar) dict
        +obtener(cliente_id, tendero_id) dict
        +crear(tendero_id, nombre, tel, dir) dict
        +actualizar(cliente_id, tendero_id, datos) dict
        +eliminar(cliente_id, tendero_id) dict
        -_serializar(cliente) dict
    }

    class DeudaService {
        +listar(tendero_id, estado, cliente_id) dict
        +obtener(deuda_id, tendero_id) dict
        +crear(tendero_id, cliente_id, productos, fecha, obs) dict
        +agregar_producto(deuda_id, tendero_id, nombre, precio, cant) dict
        +pagar(deuda_id, tendero_id) dict
        +eliminar(deuda_id, tendero_id) dict
        -_serializar_deuda(deuda) dict
    }

    class DashboardService {
        +obtener_resumen(tendero_id) dict
        +obtener_alertas(tendero_id, dias) dict
        +obtener_top_deudores(tendero_id, limite) dict
    }

    %% ── ENTIDADES DE BASE DE DATOS ────────────────────────────────────────
    class Tendero {
        +int id
        +string nombre
        +string email
        +string contrasena
        +string nombre_tienda
        +string telefono
        +bool activo
        +datetime creado_en
    }

    class Cliente {
        +int id
        +int tendero_id
        +string nombre
        +string telefono
        +string direccion
        +bool activo
        +datetime creado_en
    }

    class Deuda {
        +int id
        +int cliente_id
        +int tendero_id
        +decimal total
        +enum estado
        +date fecha_limite
        +datetime fecha_pago
        +string observaciones
        +datetime creado_en
    }

    class DetalleDeuda {
        +int id
        +int deuda_id
        +string nombre_producto
        +decimal precio
        +int cantidad
        +decimal subtotal
        +datetime creado_en
    }

    %% ── MIDDLEWARE ────────────────────────────────────────────────────────
    class AuthMiddleware {
        +hash_password(password) string
        +generate_token(tendero_id, email) string
        +token_required(f) function
    }

    %% ── RELACIONES ────────────────────────────────────────────────────────
    AuthService    --> TenderoModel    : usa
    AuthService    --> AuthMiddleware  : usa
    ClienteService --> ClienteModel   : usa
    ClienteService --> DeudaModel     : usa
    DeudaService   --> DeudaModel     : usa
    DeudaService   --> ClienteModel   : usa
    DashboardService --> DeudaModel   : usa
    DashboardService --> ClienteModel : usa

    TenderoModel --> Tendero      : persiste
    ClienteModel --> Cliente      : persiste
    DeudaModel   --> Deuda        : persiste
    DeudaModel   --> DetalleDeuda : persiste

    Tendero      "1" --> "N" Cliente      : tiene
    Cliente      "1" --> "N" Deuda        : tiene
    Deuda        "1" --> "N" DetalleDeuda : contiene
```

---

## Relaciones principales

| Relación | Tipo | Descripción |
|---|---|---|
| Tendero → Cliente | 1 a N | Un tendero tiene muchos clientes |
| Cliente → Deuda | 1 a N | Un cliente puede tener muchas deudas |
| Deuda → DetalleDeuda | 1 a N | Una deuda tiene muchos productos |
| Service → Model | Dependencia | Los servicios usan los modelos para acceder a datos |
| AuthService → Middleware | Dependencia | Usa hash y JWT para seguridad |
