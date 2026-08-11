# Casos de Uso e Historias de Usuario
## Evidencia GA8-220501096-AA1-EV01 — SENA
**Autor:** Carlos Varón | **Proyecto:** Cuenta Clara

---

## 1. Actores del sistema

| Actor | Descripción |
|---|---|
| **Tendero** | Usuario principal. Dueño de la tienda que gestiona clientes y deudas |
| **Sistema** | La aplicación Cuenta Clara |
| **Base de datos** | MySQL — persiste toda la información |

---

## 2. Casos de uso principales

```
                    ┌─────────────────────────────────┐
                    │         CUENTA CLARA             │
                    │                                  │
         ┌──────┐   │  ○ Registrarse en el sistema    │
         │      │───┼─►○ Iniciar sesión               │
         │      │   │                                  │
         │TEND- │   │  ○ Gestionar clientes           │
         │ ERO  │───┼─►  ├─ Agregar cliente           │
         │      │   │    ├─ Editar cliente             │
         │      │   │    ├─ Buscar cliente             │
         └──────┘   │    └─ Eliminar cliente           │
                    │                                  │
                    │  ○ Gestionar deudas             │
                    │───►  ├─ Registrar deuda          │
                    │      ├─ Agregar producto          │
                    │      ├─ Marcar como pagada       │
                    │      ├─ Filtrar por estado       │
                    │      └─ Eliminar deuda           │
                    │                                  │
                    │  ○ Ver dashboard                │
                    │───►  ├─ Ver resumen financiero   │
                    │      ├─ Ver alertas vencimiento  │
                    │      └─ Ver top deudores         │
                    └─────────────────────────────────┘
```

---

## 3. Historias de usuario

### HU-01: Registro de tendero
**Como** tendero,  
**quiero** crear una cuenta en Cuenta Clara,  
**para** gestionar las deudas de mi tienda digitalmente.

**Criterios de aceptación:**
- El sistema solicita nombre, nombre de tienda, email y contraseña
- La contraseña debe tener mínimo 6 caracteres
- El email debe ser único en el sistema
- Al registrarse exitosamente, el tendero accede directamente al dashboard

---

### HU-02: Inicio de sesión
**Como** tendero registrado,  
**quiero** iniciar sesión con mi email y contraseña,  
**para** acceder a la información de mi tienda.

**Criterios de aceptación:**
- El sistema valida email y contraseña
- Si las credenciales son incorrectas, muestra mensaje de error
- Al autenticarse, recibe un token JWT válido por 24 horas
- El token se usa en todas las peticiones siguientes

---

### HU-03: Registrar cliente
**Como** tendero,  
**quiero** agregar nuevos clientes a mi tienda,  
**para** llevar un registro de quiénes me compran fiado.

**Criterios de aceptación:**
- El nombre del cliente es obligatorio
- Se puede agregar teléfono y dirección opcionalmente
- No puede haber dos clientes con el mismo nombre en la misma tienda
- El cliente queda asociado únicamente a mi tienda

---

### HU-04: Registrar deuda con productos
**Como** tendero,  
**quiero** registrar lo que le fié a un cliente con sus productos,  
**para** saber exactamente cuánto me debe y qué llevó.

**Criterios de aceptación:**
- Debo seleccionar el cliente de mi lista
- Puedo agregar uno o más productos (nombre, precio, cantidad)
- El total se calcula automáticamente
- Puedo establecer una fecha límite de pago
- Puedo agregar observaciones (ej: "paga los viernes")

---

### HU-05: Marcar deuda como pagada
**Como** tendero,  
**quiero** marcar una deuda como pagada cuando el cliente me cancele,  
**para** llevar el historial de pagos actualizado.

**Criterios de aceptación:**
- Solo se pueden pagar deudas en estado pendiente o vencida
- Al pagar, se registra la fecha y hora exacta del pago
- Una deuda pagada no se puede volver a pagar
- Una deuda pagada no se puede eliminar (es historial)

---

### HU-06: Ver alertas de vencimiento
**Como** tendero,  
**quiero** ver qué deudas están vencidas o próximas a vencer,  
**para** saber a quién cobrarle con urgencia.

**Criterios de aceptación:**
- El dashboard muestra deudas ya vencidas con días de retraso
- Muestra deudas que vencen en los próximos 7 días
- Cada alerta muestra el cliente, el monto y la fecha
- Se puede ajustar el rango de días de la alerta

---

### HU-07: Ver resumen financiero
**Como** tendero,  
**quiero** ver un resumen de cuánto me deben en total,  
**para** conocer el estado financiero de mi tienda de un vistazo.

**Criterios de aceptación:**
- Muestra total de clientes activos
- Muestra monto total pendiente de cobro
- Muestra monto total vencido
- Muestra monto total ya cobrado
- Muestra los clientes que más deben (top deudores)

---

### HU-08: Buscar cliente
**Como** tendero,  
**quiero** buscar un cliente por nombre,  
**para** encontrar rápidamente su información sin revisar toda la lista.

**Criterios de aceptación:**
- La búsqueda es en tiempo real mientras escribe
- Funciona con nombre parcial (buscar "mar" encuentra "María")
- Muestra la deuda pendiente de cada cliente en los resultados

---

## 4. Requerimientos funcionales

| ID | Requerimiento | Historia |
|---|---|---|
| RF-01 | Registro de tendero con validación de datos | HU-01 |
| RF-02 | Autenticación con email y contraseña | HU-02 |
| RF-03 | Generación y validación de tokens JWT | HU-02 |
| RF-04 | CRUD completo de clientes | HU-03, HU-08 |
| RF-05 | Registro de deudas con múltiples productos | HU-04 |
| RF-06 | Cálculo automático del total de la deuda | HU-04 |
| RF-07 | Registro de pagos con fecha y hora | HU-05 |
| RF-08 | Alertas de deudas vencidas | HU-06 |
| RF-09 | Dashboard con métricas financieras | HU-07 |
| RF-10 | Búsqueda de clientes por nombre | HU-08 |

---

## 5. Requerimientos no funcionales

| ID | Requerimiento | Descripción |
|---|---|---|
| RNF-01 | Seguridad | Contraseñas cifradas con SHA-256 |
| RNF-02 | Seguridad | Autenticación con JWT |
| RNF-03 | Seguridad | Aislamiento de datos por tendero |
| RNF-04 | Usabilidad | Interfaz responsive para móvil y escritorio |
| RNF-05 | Mantenibilidad | Arquitectura por capas (MVC) |
| RNF-06 | Testabilidad | Pruebas unitarias con pytest |
| RNF-07 | Escalabilidad | API REST sin estado (stateless) |
| RNF-08 | Rendimiento | Respuesta de la API menor a 500ms |
