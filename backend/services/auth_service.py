# =============================================================================
# services/auth_service.py - Lógica de negocio de autenticación
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
#
# Esta capa contiene TODA la lógica de negocio.
# No sabe nada de HTTP, no usa request ni jsonify.
# Solo recibe datos, los procesa y retorna resultados.
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.tendero_model import TenderoModel
from middleware.auth_middleware import hash_password, generate_token


class AuthService:
    """
    Servicio de autenticación.
    Contiene las reglas de negocio para registro y login.
    """

    @staticmethod
    def registrar(nombre, email, contrasena, nombre_tienda, telefono=None):
        """
        Registra un nuevo tendero aplicando todas las reglas de negocio:
        - Validación de campos obligatorios
        - Validación de formato de email
        - Validación de longitud de contraseña
        - Verificación de email único
        - Hash de contraseña
        - Generación de token JWT

        Retorna: dict con exito, mensaje, token y datos del tendero
        """
        # ── Validaciones de negocio ────────────────────────────────────────
        nombre        = nombre.strip()        if nombre        else ''
        email         = email.strip().lower() if email         else ''
        contrasena    = contrasena.strip()    if contrasena    else ''
        nombre_tienda = nombre_tienda.strip() if nombre_tienda else ''

        if not nombre or not email or not contrasena or not nombre_tienda:
            return {'exito': False,
                    'mensaje': 'Todos los campos obligatorios deben completarse.',
                    'codigo': 400}

        if '@' not in email or '.' not in email:
            return {'exito': False,
                    'mensaje': 'El email no tiene un formato válido.',
                    'codigo': 400}

        if len(contrasena) < 6:
            return {'exito': False,
                    'mensaje': 'La contraseña debe tener mínimo 6 caracteres.',
                    'codigo': 400}

        if len(nombre) < 2:
            return {'exito': False,
                    'mensaje': 'El nombre debe tener al menos 2 caracteres.',
                    'codigo': 400}

        # ── Regla de negocio: email único ──────────────────────────────────
        if TenderoModel.buscar_por_email(email):
            return {'exito': False,
                    'mensaje': f'El email "{email}" ya está registrado.',
                    'codigo': 409}

        # ── Crear tendero ──────────────────────────────────────────────────
        nuevo_id = TenderoModel.crear(
            nombre, email,
            hash_password(contrasena),
            nombre_tienda,
            telefono.strip() if telefono else None
        )

        token = generate_token(nuevo_id, email)

        return {
            'exito'  : True,
            'mensaje': f'Tendero "{nombre}" registrado exitosamente.',
            'codigo' : 201,
            'token'  : token,
            'tendero': {
                'id'           : nuevo_id,
                'nombre'       : nombre,
                'email'        : email,
                'nombre_tienda': nombre_tienda
            }
        }

    @staticmethod
    def login(email, contrasena):
        """
        Autentica al tendero verificando sus credenciales.

        Retorna: dict con exito, mensaje, token y datos del tendero
        """
        email      = email.strip().lower()    if email      else ''
        contrasena = contrasena.strip()       if contrasena else ''

        if not email or not contrasena:
            return {'exito': False,
                    'mensaje': 'Email y contraseña son obligatorios.',
                    'codigo': 400}

        tendero = TenderoModel.buscar_por_credenciales(
            email, hash_password(contrasena)
        )

        if not tendero:
            return {'exito': False,
                    'mensaje': 'Email o contraseña incorrectos.',
                    'codigo': 401}

        token = generate_token(tendero['id'], tendero['email'])

        return {
            'exito'  : True,
            'mensaje': f'Bienvenido, {tendero["nombre"]}.',
            'codigo' : 200,
            'token'  : token,
            'tendero': {
                'id'           : tendero['id'],
                'nombre'       : tendero['nombre'],
                'email'        : tendero['email'],
                'nombre_tienda': tendero['nombre_tienda'],
                'telefono'     : tendero['telefono']
            }
        }

    @staticmethod
    def obtener_perfil(tendero_id):
        """Obtiene el perfil del tendero autenticado."""
        tendero = TenderoModel.buscar_por_id(tendero_id)

        if not tendero:
            return {'exito': False, 'mensaje': 'Tendero no encontrado.', 'codigo': 404}

        tendero['creado_en'] = str(tendero['creado_en'])
        return {'exito': True, 'codigo': 200, 'tendero': tendero}
