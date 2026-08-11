# Documentación de Ambientes
## Evidencia GA8-220501096-AA1-EV01 — SENA
**Autor:** Carlos Varón | **Proyecto:** Cuenta Clara

---

## 1. Ambiente de Desarrollo

### 1.1 Especificaciones del equipo

| Componente | Especificación |
|---|---|
| Sistema Operativo | Windows 10/11 64-bit |
| Procesador | Compatible x64 |
| RAM mínima | 4 GB |
| Espacio en disco | 500 MB libres |

### 1.2 Software requerido

| Software | Versión | Propósito | Descarga |
|---|---|---|---|
| Python | 3.8 o superior | Backend Flask | python.org |
| MySQL Server | 8.0 | Base de datos | mysql.com |
| MySQL Workbench | 8.0 | Gestión BD | mysql.com |
| VS Code | Última | IDE de desarrollo | code.visualstudio.com |
| Postman | Última | Testing de API | postman.com |
| Git | 2.x | Control de versiones | git-scm.com |

### 1.3 Extensiones de VS Code recomendadas

| Extensión | Propósito |
|---|---|
| Python | Soporte Python |
| Pylance | Autocompletado Python |
| GitLens | Control de versiones |
| Thunder Client | Testing API (alternativa a Postman) |
| MySQL (cweijan) | Gestión BD desde VS Code |

### 1.4 Dependencias Python (requirements.txt)

```
Flask==3.0.3
mysql-connector-python==8.4.0
PyJWT==2.8.0
flask-cors==4.0.1
pytest==9.1.1
```

### 1.5 Configuración del entorno

**Variables de configuración** (`backend/config.py`):

```python
DB_HOST     = 'localhost'
DB_PORT     = 3306          # o 3307 según instalación
DB_NAME     = 'cuenta_clara'
DB_USER     = 'root'
DB_PASSWORD = 'tu_contraseña'
JWT_SECRET  = 'cuenta_clara_secret_key_2024'
JWT_EXPIRATION_HOURS = 24
DEBUG       = True
PORT        = 5000
```

### 1.6 Instrucciones de instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/cuenta-clara.git
cd cuenta-clara

# 2. Crear entorno virtual
cd backend
python -m venv venv

# 3. Activar entorno virtual (Windows)
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar base de datos
# Abrir MySQL Workbench y ejecutar database/cuenta_clara.sql

# 6. Configurar credenciales en backend/config.py

# 7. Ejecutar el servidor
python app.py
```

---

## 2. Ambiente de Pruebas

### 2.1 Herramientas de pruebas

| Herramienta | Versión | Propósito |
|---|---|---|
| pytest | 9.1.1 | Pruebas unitarias automatizadas |
| unittest.mock | Estándar Python | Simulación de dependencias |
| Postman | Última | Pruebas manuales de la API |

### 2.2 Estructura de pruebas

```
backend/tests/
├── __init__.py          ← Marca la carpeta como paquete Python
├── test_auth.py         ← 12 pruebas del módulo de autenticación
├── test_clientes.py     ← 10 pruebas del módulo de clientes
└── test_deudas.py       ← 11 pruebas del módulo de deudas
```

### 2.3 Ejecución de pruebas

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar solo un módulo
pytest tests/test_auth.py -v

# Ejecutar con reporte de cobertura
pytest tests/ -v --tb=short

# Resultado esperado:
# 33 passed in X.XXs
```

### 2.4 Resultados de pruebas obtenidos

| Módulo | Pruebas | Estado |
|---|---|---|
| test_auth.py | 12 | ✅ 12 passed |
| test_clientes.py | 10 | ✅ 10 passed |
| test_deudas.py | 11 | ✅ 11 passed |
| **TOTAL** | **33** | **✅ 33 passed** |

### 2.5 Casos de prueba cubiertos

**Módulo Auth (12 pruebas):**
- Registro con campos vacíos → rechaza correctamente
- Registro con email inválido → rechaza correctamente
- Registro con contraseña corta → rechaza correctamente
- Registro con nombre muy corto → rechaza correctamente
- Registro con email duplicado → rechaza con 409
- Registro exitoso → crea tendero y retorna token
- Login con campos vacíos → rechaza correctamente
- Login con credenciales incorrectas → rechaza con 401
- Login exitoso → retorna token JWT
- Hash consistente → mismo texto produce mismo hash
- Hash diferente → textos diferentes producen hashes distintos
- Longitud del hash → SHA-256 siempre produce 64 caracteres

**Módulo Clientes (10 pruebas):**
- Crear con nombre vacío → rechaza
- Crear con nombre muy corto → rechaza
- Crear con nombre duplicado → rechaza con 409
- Crear exitoso → retorna cliente con ID
- Eliminar cliente inexistente → 404
- Eliminar con deudas activas → rechaza con 409
- Eliminar sin deudas → elimina correctamente
- Actualizar sin campos → rechaza
- Actualizar exitoso → confirma actualización

**Módulo Deudas (11 pruebas):**
- Crear sin cliente → rechaza
- Crear sin productos → rechaza
- Crear producto sin nombre → rechaza
- Crear con precio inválido → rechaza
- Crear con cantidad inválida → rechaza
- Crear con cliente inexistente → 404
- Crear exitoso → retorna deuda con total calculado
- Pagar deuda inexistente → 404
- Pagar deuda ya pagada → rechaza con 409
- Pagar exitoso → marca como pagada
- Eliminar deuda pagada → rechaza con 409
- Eliminar deuda pendiente → elimina correctamente

### 2.6 Estrategia de mocking

Las pruebas usan `unittest.mock.patch` para simular:
- La capa de modelos (no se conecta a MySQL real)
- La generación de tokens JWT
- El hash de contraseñas

Esto permite ejecutar las pruebas sin necesidad de tener MySQL activo.

---

## 3. Control de versiones

### 3.1 Configuración de Git

```bash
# Inicializar repositorio
git init

# Configurar usuario
git config user.name "Carlos Varón"
git config user.email "tu@email.com"

# Primer commit
git add .
git commit -m "feat: Cuenta Clara - GA8-220501096-AA1-EV01"

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/cuenta-clara.git
git branch -M main
git push -u origin main
```

### 3.2 Estructura de ramas recomendada

```
main          ← Código estable para entrega
  └── dev     ← Desarrollo activo
        ├── feature/auth
        ├── feature/clientes
        └── feature/deudas
```

### 3.3 Convención de commits

```
feat:     Nueva funcionalidad
fix:      Corrección de bug
docs:     Documentación
test:     Pruebas unitarias
refactor: Refactorización de código
```

---

## 4. Arquitectura y patrones aplicados

### 4.1 Arquitectura por capas

```
Presentación  → routes/       (HTTP handlers)
Negocio       → services/     (reglas de negocio)
Datos         → models/       (acceso a MySQL)
Seguridad     → middleware/   (JWT + SHA-256)
```

### 4.2 Patrones de diseño aplicados

| Patrón | Dónde | Para qué |
|---|---|---|
| **Repository** | models/ | Encapsula el acceso a datos |
| **Service Layer** | services/ | Centraliza la lógica de negocio |
| **Blueprint** | routes/ | Organiza endpoints por módulo |
| **Decorator** | @token_required | Protege endpoints con JWT |
| **Factory** | conftest.py | Crea mocks para pruebas |

### 4.3 Mecanismos de seguridad

| Mecanismo | Implementación |
|---|---|
| Cifrado de contraseñas | SHA-256 (hashlib) |
| Autenticación | JWT Bearer Token |
| Autorización | Decorador @token_required |
| Aislamiento de datos | Filtro por tendero_id en todas las consultas |
| Eliminación segura | Lógica (activo=FALSE) en lugar de física |
