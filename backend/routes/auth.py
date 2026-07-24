# =============================================================================
# routes/auth.py - Endpoints de autenticación
# Proyecto: Cuenta Clara
# Evidencia: GA7-220501096-AA5-EV03 - SENA
# Autor: Carlos Varón
#
# Endpoints:
#   POST /api/auth/registro  → Registrar nuevo tendero
#   POST /api/auth/login     → Iniciar sesión y obtener token JWT
#   GET  /api/auth/perfil    → Ver perfil del tendero autenticado
# =============================================================================

from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import execute_query
from middleware.auth_middleware import hash_password, generate_token, token_required

# Blueprint: agrupa los endpoints de autenticación bajo el prefijo /api/auth
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# =============================================================================
# ENDPOINT 1: Registro de tendero
# Método:  POST
# URL:     /api/auth/registro
# Acceso:  Público (no requiere token)
# =============================================================================
@auth_bp.route('/registro', methods=['POST'])
def registro():
    """
    Registra un nuevo tendero en el sistema.

    Body JSON requerido:
    {
        "nombre":        "Carlos Varón",
        "email":         "carlos@tienda.com",
        "contrasena":    "miClave123",
        "nombre_tienda": "Tienda Don Carlos",
        "telefono":      "3001234567"   (opcional)
    }
    """
    data = request.get_json()

    # ── Validaciones ───────────────────────────────────────────────────────────
    if not data:
        return jsonify({'exito': False,
                        'mensaje': 'No se recibieron datos.'}), 400

    campos_requeridos = ['nombre', 'email', 'contrasena', 'nombre_tienda']
    for campo in campos_requeridos:
        if not data.get(campo, '').strip():
            return jsonify({'exito': False,
                            'mensaje': f'El campo "{campo}" es obligatorio.'}), 400

    nombre        = data['nombre'].strip()
    email         = data['email'].strip().lower()
    contrasena    = data['contrasena'].strip()
    nombre_tienda = data['nombre_tienda'].strip()
    telefono      = data.get('telefono', '').strip()

    if len(contrasena) < 6:
        return jsonify({'exito': False,
                        'mensaje': 'La contraseña debe tener mínimo 6 caracteres.'}), 400

    if '@' not in email:
        return jsonify({'exito': False,
                        'mensaje': 'El email no tiene un formato válido.'}), 400

    # ── Verificar que el email no esté ya registrado ───────────────────────────
    try:
        existente = execute_query(
            "SELECT id FROM tenderos WHERE email = %s",
            (email,),
            fetch_one=True
        )
        if existente:
            return jsonify({'exito': False,
                            'mensaje': f'El email "{email}" ya está registrado.'}), 409

        # ── Insertar el nuevo tendero ───────────────────────────────────────────
        nuevo_id = execute_query(
            """INSERT INTO tenderos (nombre, email, contrasena, nombre_tienda, telefono)
               VALUES (%s, %s, %s, %s, %s)""",
            (nombre, email, hash_password(contrasena), nombre_tienda, telefono)
        )

        # ── Generar token JWT para que pueda usar la app inmediatamente ────────
        token = generate_token(nuevo_id, email)

        return jsonify({
            'exito'   : True,
            'mensaje' : f'Tendero "{nombre}" registrado exitosamente.',
            'token'   : token,
            'tendero' : {
                'id'           : nuevo_id,
                'nombre'       : nombre,
                'email'        : email,
                'nombre_tienda': nombre_tienda
            }
        }), 201

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 2: Login del tendero
# Método:  POST
# URL:     /api/auth/login
# Acceso:  Público (no requiere token)
# =============================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autentica al tendero y retorna un token JWT.

    Body JSON requerido:
    {
        "email":      "carlos@tienda.com",
        "contrasena": "miClave123"
    }

    Respuesta exitosa:
    {
        "exito": true,
        "mensaje": "Bienvenido, Carlos Varón.",
        "token": "eyJ...",
        "tendero": { "id": 1, "nombre": "...", "nombre_tienda": "..." }
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'exito': False,
                        'mensaje': 'No se recibieron datos.'}), 400

    email      = data.get('email', '').strip().lower()
    contrasena = data.get('contrasena', '').strip()

    if not email or not contrasena:
        return jsonify({'exito': False,
                        'mensaje': 'Email y contraseña son obligatorios.'}), 400

    try:
        # Buscar tendero por email Y hash de contraseña
        tendero = execute_query(
            """SELECT id, nombre, email, nombre_tienda, telefono
               FROM tenderos
               WHERE email = %s AND contrasena = %s AND activo = TRUE""",
            (email, hash_password(contrasena)),
            fetch_one=True
        )

        if not tendero:
            return jsonify({'exito': False,
                            'mensaje': 'Email o contraseña incorrectos.'}), 401

        # Generar token JWT
        token = generate_token(tendero['id'], tendero['email'])

        return jsonify({
            'exito'  : True,
            'mensaje': f'Bienvenido, {tendero["nombre"]}.',
            'token'  : token,
            'tendero': {
                'id'           : tendero['id'],
                'nombre'       : tendero['nombre'],
                'email'        : tendero['email'],
                'nombre_tienda': tendero['nombre_tienda'],
                'telefono'     : tendero['telefono']
            }
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 3: Ver perfil del tendero autenticado
# Método:  GET
# URL:     /api/auth/perfil
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@auth_bp.route('/perfil', methods=['GET'])
@token_required
def perfil(tendero_id):
    """
    Retorna los datos del tendero autenticado.
    Requiere header: Authorization: Bearer <token>
    """
    try:
        tendero = execute_query(
            """SELECT id, nombre, email, nombre_tienda, telefono, creado_en
               FROM tenderos WHERE id = %s""",
            (tendero_id,),
            fetch_one=True
        )

        if not tendero:
            return jsonify({'exito': False,
                            'mensaje': 'Tendero no encontrado.'}), 404

        # Convertir datetime a string para que JSON pueda serializarlo
        tendero['creado_en'] = str(tendero['creado_en'])

        return jsonify({
            'exito'  : True,
            'tendero': tendero
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500
