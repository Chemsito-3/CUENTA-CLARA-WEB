# =============================================================================
# app.py - Punto de entrada principal de la aplicación
# Proyecto: Cuenta Clara
# Evidencia: GA7-220501096-AA5-EV03 - SENA
# Autor: Carlos Varón
#
# CÓMO EJECUTAR:
#   cd backend
#   venv\Scripts\activate
#   python app.py
# =============================================================================

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# ── Importar los blueprints (módulos de rutas) ─────────────────────────────
from routes.auth      import auth_bp
from routes.clientes  import clientes_bp
from routes.deudas    import deudas_bp
from routes.dashboard import dashboard_bp

# ── Crear la aplicación Flask ──────────────────────────────────────────────
app = Flask(__name__)

# ── Habilitar CORS ─────────────────────────────────────────────────────────
# Permite que el frontend HTML consuma la API desde el navegador
CORS(app)

# ── Registrar blueprints ───────────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(deudas_bp)
app.register_blueprint(dashboard_bp)


# ── Endpoint raíz: bienvenida y estado de la API ───────────────────────────
@app.route('/')
def index():
    return jsonify({
        'proyecto'  : 'Cuenta Clara',
        'version'   : '1.0.0',
        'estado'    : 'activo',
        'evidencia' : 'GA7-220501096-AA5-EV03',
        'endpoints' : {
            'auth'     : '/api/auth',
            'clientes' : '/api/clientes',
            'deudas'   : '/api/deudas',
            'dashboard': '/api/dashboard'
        }
    }), 200


# ── Manejadores de errores globales ───────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({'exito': False,
                    'mensaje': 'Endpoint no encontrado.'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'exito': False,
                    'mensaje': 'Método HTTP no permitido en este endpoint.'}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'exito': False,
                    'mensaje': 'Error interno del servidor.'}), 500


# ── Punto de entrada ───────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  Cuenta Clara API - GA7-220501096-AA5-EV03")
    print("  Autor: Carlos Varón")
    print("=" * 60)
    print("  Servidor: http://localhost:5000")
    print()
    print("  Endpoints disponibles:")
    print("    GET  /                            → Estado de la API")
    print("    POST /api/auth/registro           → Registrar tendero")
    print("    POST /api/auth/login              → Iniciar sesión")
    print("    GET  /api/auth/perfil             → Ver perfil")
    print("    GET  /api/clientes/               → Listar clientes")
    print("    POST /api/clientes/               → Crear cliente")
    print("    GET  /api/clientes/<id>           → Ver cliente")
    print("    PUT  /api/clientes/<id>           → Actualizar cliente")
    print("    DELETE /api/clientes/<id>         → Eliminar cliente")
    print("    GET  /api/deudas/                 → Listar deudas")
    print("    POST /api/deudas/                 → Crear deuda")
    print("    GET  /api/deudas/<id>             → Ver deuda")
    print("    POST /api/deudas/<id>/productos   → Agregar producto")
    print("    PATCH /api/deudas/<id>/pagar      → Pagar deuda")
    print("    DELETE /api/deudas/<id>           → Eliminar deuda")
    print("    GET  /api/dashboard/              → Resumen general")
    print("    GET  /api/dashboard/alertas       → Alertas vencimiento")
    print("    GET  /api/dashboard/top           → Top clientes")
    print("=" * 60)
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=Config.PORT)
