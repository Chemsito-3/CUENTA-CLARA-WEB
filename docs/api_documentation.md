# Documentación de la API — Cuenta Clara
**Evidencia:** GA7-220501096-AA5-EV03 — SENA  
**Autor:** Carlos Varón  
**Versión:** 1.0.0  
**URL Base:** `http://localhost:5000`  
**Formato:** JSON  
**Autenticación:** Bearer Token (JWT)

---

## Resumen de los 18 endpoints

| # | Método | Endpoint | Descripción | Auth |
|---|--------|----------|-------------|------|
| 1 | POST | /api/auth/registro | Registrar tendero | ❌ |
| 2 | POST | /api/auth/login | Iniciar sesión | ❌ |
| 3 | GET | /api/auth/perfil | Ver perfil | ✅ |
| 4 | GET | /api/clientes/ | Listar clientes | ✅ |
| 5 | GET | /api/clientes/{id} | Ver cliente | ✅ |
| 6 | POST | /api/clientes/ | Crear cliente | ✅ |
| 7 | PUT | /api/clientes/{id} | Actualizar cliente | ✅ |
| 8 | DELETE | /api/clientes/{id} | Eliminar cliente | ✅ |
| 9 | GET | /api/deudas/ | Listar deudas | ✅ |
| 10 | GET | /api/deudas/{id} | Ver deuda | ✅ |
| 11 | POST | /api/deudas/ | Crear deuda | ✅ |
| 12 | POST | /api/deudas/{id}/productos | Agregar producto | ✅ |
| 13 | PATCH | /api/deudas/{id}/pagar | Registrar pago | ✅ |
| 14 | DELETE | /api/deudas/{id} | Eliminar deuda | ✅ |
| 15 | GET | /api/dashboard/resumen | Resumen general | ✅ |
| 16 | GET | /api/dashboard/alertas | Alertas vencimiento | ✅ |
| 17 | GET | /api/dashboard/top-deudores | Top deudores | ✅ |
| 18 | GET | /health | Estado del servidor | ❌ |

---

## 1. POST /api/auth/registro
Registra una nueva cuenta de tendero.

**Body:**
```json
{
    "nombre": "Carlos Varón",
    "email": "carlos@tienda.com",
    "contrasena": "tienda123",
    "nombre_tienda": "Tienda Don Carlos",
    "telefono": "3001234567"
}
```
**Respuesta 201:**
```json
{
    "exito": true,
    "mensaje": "Tendero registrado exitosamente.",
    "token": "eyJhbGci...",
    "tendero": { "id": 1, "nombre": "Carlos Varón", "nombre_tienda": "Tienda Don Carlos" }
}
```
**Errores:** 400 campos vacíos · 409 email duplicado

---

## 2. POST /api/auth/login
Autentica al tendero y retorna token JWT (válido 24h).

**Body:**
```json
{ "email": "carlos@tienda.com", "contrasena": "tienda123" }
```
**Respuesta 200:**
```json
{
    "exito": true,
    "mensaje": "Bienvenido, Carlos Varón.",
    "token": "eyJhbGci...",
    "tendero": { "id": 1, "nombre": "Carlos Varón", "nombre_tienda": "Tienda Don Carlos" }
}
```
**Errores:** 400 campos vacíos · 401 credenciales incorrectas

---

## 3. GET /api/auth/perfil 🔒
Retorna datos del tendero autenticado.

**Header:** `Authorization: Bearer <token>`

**Respuesta 200:**
```json
{
    "exito": true,
    "tendero": { "id": 1, "nombre": "Carlos Varón", "email": "carlos@tienda.com", "nombre_tienda": "Tienda Don Carlos" }
}
```

---

## 4. GET /api/clientes/ 🔒
Lista todos los clientes activos con resumen de deudas.

**Query params:** `?buscar=nombre`

**Respuesta 200:**
```json
{
    "exito": true, "total": 3,
    "clientes": [{ "id": 1, "nombre": "María López", "deuda_pendiente": 14000.0, "deuda_vencida": 0.0 }]
}
```

---

## 5. GET /api/clientes/{id} 🔒
Detalle de cliente con resumen y deudas activas.

**Respuesta 200:**
```json
{
    "exito": true,
    "cliente": { "id": 1, "nombre": "María López", "telefono": "3109876543" },
    "resumen_deudas": { "total_deudas": 1, "pendiente": 14000.0, "vencida": 0.0, "pagada": 0.0 },
    "deudas_activas": [...]
}
```
**Errores:** 404 no encontrado

---

## 6. POST /api/clientes/ 🔒
Crea un nuevo cliente en la tienda.

**Body:**
```json
{ "nombre": "Pedro Gómez", "telefono": "3101234567", "direccion": "Calle 10 # 5-20" }
```
**Respuesta 201:**
```json
{ "exito": true, "mensaje": "Cliente creado exitosamente.", "cliente": { "id": 4, "nombre": "Pedro Gómez" } }
```
**Errores:** 400 nombre vacío · 409 nombre duplicado

---

## 7. PUT /api/clientes/{id} 🔒
Actualiza datos del cliente. Solo modifica los campos enviados.

**Body (todos opcionales):**
```json
{ "nombre": "Pedro Gómez R.", "telefono": "3209999999", "direccion": "Carrera 8 # 3-10" }
```
**Respuesta 200:**
```json
{ "exito": true, "mensaje": "Cliente actualizado exitosamente." }
```

---

## 8. DELETE /api/clientes/{id} 🔒
Eliminación lógica del cliente. Falla si tiene deudas pendientes.

**Respuesta 200:**
```json
{ "exito": true, "mensaje": "Cliente eliminado exitosamente." }
```
**Errores:** 404 no encontrado · 409 tiene deudas pendientes

---

## 9. GET /api/deudas/ 🔒
Lista deudas con filtros opcionales.

**Query params:** `?estado=pendiente|pagada|vencida` · `?cliente_id=1`

**Respuesta 200:**
```json
{
    "exito": true, "total": 2,
    "deudas": [{ "id": 1, "total": 14000.0, "estado": "pendiente", "cliente_nombre": "María López", "cantidad_productos": 3 }]
}
```

---

## 10. GET /api/deudas/{id} 🔒
Detalle completo de deuda con lista de productos.

**Respuesta 200:**
```json
{
    "exito": true,
    "deuda": { "id": 1, "total": 14000.0, "estado": "pendiente", "cliente_nombre": "María López" },
    "productos": [{ "nombre_producto": "Arroz x 500g", "precio": 3500.0, "cantidad": 2, "subtotal": 7000.0 }]
}
```

---

## 11. POST /api/deudas/ 🔒
Registra una nueva deuda con uno o más productos.

**Body:**
```json
{
    "cliente_id": 4,
    "fecha_limite": "2024-12-31",
    "observaciones": "Paga los viernes",
    "productos": [
        { "nombre_producto": "Arroz x 500g", "precio": 3500, "cantidad": 2 },
        { "nombre_producto": "Aceite 250ml",  "precio": 4200, "cantidad": 1 }
    ]
}
```
**Respuesta 201:**
```json
{ "exito": true, "mensaje": "Deuda registrada.", "deuda_id": 5, "total": 11200.0 }
```
**Errores:** 400 sin productos · 404 cliente no encontrado

---

## 12. POST /api/deudas/{id}/productos 🔒
Agrega un producto a una deuda existente pendiente.

**Body:**
```json
{ "nombre_producto": "Gaseosa 1.5L", "precio": 5000, "cantidad": 2 }
```
**Respuesta 201:**
```json
{ "exito": true, "mensaje": "Producto agregado.", "subtotal": 10000.0 }
```
**Errores:** 409 deuda ya pagada

---

## 13. PATCH /api/deudas/{id}/pagar 🔒
Marca la deuda como pagada y registra la fecha del pago.

**Respuesta 200:**
```json
{ "exito": true, "mensaje": "Deuda pagada.", "total_pagado": 11200.0, "fecha_pago": "2024-06-30 18:45:23" }
```
**Errores:** 409 ya estaba pagada

---

## 14. DELETE /api/deudas/{id} 🔒
Elimina deuda pendiente y sus productos (CASCADE).

**Respuesta 200:**
```json
{ "exito": true, "mensaje": "Deuda eliminada exitosamente." }
```
**Errores:** 409 no se puede eliminar deuda pagada

---

## 15. GET /api/dashboard/resumen 🔒
Métricas generales del negocio.

**Respuesta 200:**
```json
{
    "exito": true,
    "resumen": {
        "clientes_activos": 3,
        "deudas": { "monto_pendiente": 60000.0, "monto_vencido": 14500.0, "monto_cobrado": 10500.0 },
        "proximas_a_vencer": { "total_deudas": 2, "monto": 25000.0 }
    }
}
```

---

## 16. GET /api/dashboard/alertas 🔒
Deudas vencidas y próximas a vencer.

**Query params:** `?dias=7` (días hacia adelante, default 7)

**Respuesta 200:**
```json
{
    "exito": true,
    "alertas": {
        "vencidas": { "total": 1, "deudas": [{ "cliente_nombre": "Juan Pérez", "dias_vencida": 5 }] },
        "proximas_a_vencer": { "dias_revisados": 7, "total": 1, "deudas": [{ "cliente_nombre": "María López", "dias_restantes": 3 }] }
    }
}
```

---

## 17. GET /api/dashboard/top-deudores 🔒
Clientes ordenados por monto de deuda pendiente.

**Query params:** `?limite=5` (default 5, máx 20)

**Respuesta 200:**
```json
{
    "exito": true,
    "top_deudores": [{ "nombre": "Juan Pérez", "deuda_total": 25000.0, "total_deudas": 2 }]
}
```

---

## 18. GET /health
Estado del servidor y conexión a la base de datos.

**Respuesta 200:**
```json
{ "estado": "OK", "mensaje": "Servidor activo y conexión a BD exitosa." }
```
