# =============================================================================
# auth_middleware.py - Middleware de autenticación JWT
# Proyecto: Cuenta Clara
# =============================================================================

import jwt
import hashlib
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def hash_password(password: str) -> str:
    """Encripta una contraseña con SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_token(tendero_id: int, email: str) -> str:
    """
    Genera un token JWT para el tendero autenticado.

    El token contiene:
    - sub: ID del tendero (sujeto)
    - email: correo del tendero
    - exp: fecha de expiración (24 horas)
    - iat: fecha de emisión
    """
    payload = {
        'sub'   : tendero_id,
        'email' : email,
        'exp'   : datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat'   : datetime.utcnow()
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')


def token_required(f):
    """
    Decorador que protege los endpoints que requieren autenticación.

    Uso:
        @app.route('/clientes')
        @token_required
        def get_clientes(tendero_id):
            ...

    El token debe enviarse en el header:
        Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obtener el header Authorization
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'exito'  : False,
                'mensaje': 'Token de autenticación requerido.'
            }), 401

        token = auth_header.split(' ')[1]

        try:
            # Decodificar y verificar el token
            payload = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=['HS256']
            )
            # Pasar el tendero_id a la función del endpoint
            return f(tendero_id=payload['sub'], *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({
                'exito'  : False,
                'mensaje': 'El token ha expirado. Inicia sesión nuevamente.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'exito'  : False,
                'mensaje': 'Token inválido.'
            }), 401

    return decorated
