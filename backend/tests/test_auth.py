# =============================================================================
# tests/test_auth.py - Pruebas unitarias del módulo de autenticación
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
#
# CÓMO EJECUTAR:
#   cd backend
#   pip install pytest
#   pytest tests/ -v
# =============================================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from services.auth_service      import AuthService
from middleware.auth_middleware  import hash_password


# =============================================================================
# PRUEBAS DE REGISTRO
# =============================================================================

class TestRegistro:
    """Pruebas unitarias para el registro de tenderos."""

    def test_registro_campos_vacios(self):
        """Debe rechazar el registro si hay campos vacíos."""
        resultado = AuthService.registrar('', '', '', '')
        assert resultado['exito']  == False
        assert resultado['codigo'] == 400
        assert 'obligatorios' in resultado['mensaje']

    def test_registro_email_invalido(self):
        """Debe rechazar un email sin @ o sin punto."""
        resultado = AuthService.registrar(
            'Carlos', 'correo-invalido', 'clave123', 'Tienda'
        )
        assert resultado['exito']  == False
        assert resultado['codigo'] == 400
        assert 'email' in resultado['mensaje'].lower()

    def test_registro_contrasena_corta(self):
        """Debe rechazar contraseñas con menos de 6 caracteres."""
        resultado = AuthService.registrar(
            'Carlos', 'carlos@test.com', '123', 'Tienda'
        )
        assert resultado['exito']  == False
        assert resultado['codigo'] == 400
        assert '6' in resultado['mensaje']

    def test_registro_nombre_muy_corto(self):
        """Debe rechazar nombres con menos de 2 caracteres."""
        resultado = AuthService.registrar(
            'C', 'carlos@test.com', 'clave123', 'Tienda'
        )
        assert resultado['exito']  == False
        assert resultado['codigo'] == 400

    @patch('services.auth_service.TenderoModel')
    def test_registro_email_duplicado(self, mock_model):
        """Debe rechazar registro si el email ya existe."""
        mock_model.buscar_por_email.return_value = {'id': 1}
        resultado = AuthService.registrar(
            'Carlos', 'existe@test.com', 'clave123', 'Tienda'
        )
        assert resultado['exito']  == False
        assert resultado['codigo'] == 409
        assert 'registrado' in resultado['mensaje']

    @patch('services.auth_service.TenderoModel')
    @patch('services.auth_service.generate_token')
    def test_registro_exitoso(self, mock_token, mock_model):
        """Debe registrar correctamente un tendero válido."""
        mock_model.buscar_por_email.return_value = None
        mock_model.crear.return_value            = 5
        mock_token.return_value                  = 'token_fake_123'

        resultado = AuthService.registrar(
            'Carlos Varón', 'nuevo@test.com', 'clave123', 'Mi Tienda'
        )
        assert resultado['exito']              == True
        assert resultado['codigo']             == 201
        assert resultado['token']              == 'token_fake_123'
        assert resultado['tendero']['id']      == 5
        assert resultado['tendero']['nombre']  == 'Carlos Varón'


# =============================================================================
# PRUEBAS DE LOGIN
# =============================================================================

class TestLogin:
    """Pruebas unitarias para el inicio de sesión."""

    def test_login_campos_vacios(self):
        """Debe rechazar login con campos vacíos."""
        resultado = AuthService.login('', '')
        assert resultado['exito']  == False
        assert resultado['codigo'] == 400

    @patch('services.auth_service.TenderoModel')
    def test_login_credenciales_incorrectas(self, mock_model):
        """Debe rechazar login si las credenciales no coinciden."""
        mock_model.buscar_por_credenciales.return_value = None
        resultado = AuthService.login('carlos@test.com', 'claveMALA')
        assert resultado['exito']  == False
        assert resultado['codigo'] == 401
        assert 'incorrectos' in resultado['mensaje']

    @patch('services.auth_service.TenderoModel')
    @patch('services.auth_service.generate_token')
    def test_login_exitoso(self, mock_token, mock_model):
        """Debe autenticar correctamente con credenciales válidas."""
        mock_model.buscar_por_credenciales.return_value = {
            'id': 1, 'nombre': 'Carlos', 'email': 'carlos@test.com',
            'nombre_tienda': 'Tienda', 'telefono': '3001234567'
        }
        mock_token.return_value = 'token_valido_456'

        resultado = AuthService.login('carlos@test.com', 'clave123')
        assert resultado['exito']         == True
        assert resultado['codigo']        == 200
        assert resultado['token']         == 'token_valido_456'
        assert 'Bienvenido' in resultado['mensaje']


# =============================================================================
# PRUEBAS DE UTILIDADES
# =============================================================================

class TestUtilidades:
    """Pruebas para funciones auxiliares."""

    def test_hash_password_consistente(self):
        """El mismo texto siempre produce el mismo hash."""
        assert hash_password('admin123') == hash_password('admin123')

    def test_hash_password_diferente(self):
        """Contraseñas diferentes producen hashes diferentes."""
        assert hash_password('clave1') != hash_password('clave2')

    def test_hash_password_longitud(self):
        """SHA-256 siempre produce 64 caracteres hexadecimales."""
        resultado = hash_password('cualquier_texto')
        assert len(resultado) == 64
