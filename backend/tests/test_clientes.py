# =============================================================================
# tests/test_clientes.py - Pruebas unitarias del módulo de clientes
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from services.cliente_service import ClienteService


class TestCrearCliente:
    """Pruebas para la creación de clientes."""

    def test_nombre_vacio(self):
        """Debe rechazar cliente sin nombre."""
        r = ClienteService.crear(1, '', '3001234567', 'Calle 1')
        assert r['exito']  == False
        assert r['codigo'] == 400

    def test_nombre_muy_corto(self):
        """Debe rechazar nombre de 1 solo caracter."""
        r = ClienteService.crear(1, 'A', '', '')
        assert r['exito']  == False
        assert r['codigo'] == 400

    @patch('services.cliente_service.ClienteModel')
    def test_nombre_duplicado(self, mock_model):
        """Debe rechazar cliente con nombre ya existente en la tienda."""
        mock_model.buscar_por_nombre.return_value = {'id': 3}
        r = ClienteService.crear(1, 'María López', '', '')
        assert r['exito']  == False
        assert r['codigo'] == 409
        assert 'ya tienes' in r['mensaje'].lower()

    @patch('services.cliente_service.ClienteModel')
    def test_crear_exitoso(self, mock_model):
        """Debe crear correctamente un cliente válido."""
        mock_model.buscar_por_nombre.return_value = None
        mock_model.crear.return_value             = 7
        r = ClienteService.crear(1, 'Pedro Gómez', '3101234567', 'Calle 5')
        assert r['exito']             == True
        assert r['codigo']            == 201
        assert r['cliente']['id']     == 7
        assert r['cliente']['nombre'] == 'Pedro Gómez'


class TestEliminarCliente:
    """Pruebas para la eliminación de clientes."""

    @patch('services.cliente_service.ClienteModel')
    def test_cliente_no_encontrado(self, mock_model):
        """Debe retornar 404 si el cliente no existe."""
        mock_model.buscar_por_id.return_value = None
        r = ClienteService.eliminar(99, 1)
        assert r['exito']  == False
        assert r['codigo'] == 404

    @patch('services.cliente_service.ClienteModel')
    def test_no_eliminar_con_deudas(self, mock_model):
        """No debe eliminar cliente con deudas pendientes."""
        mock_model.buscar_por_id.return_value       = {'id': 1, 'nombre': 'María'}
        mock_model.contar_deudas_activas.return_value = 2
        r = ClienteService.eliminar(1, 1)
        assert r['exito']  == False
        assert r['codigo'] == 409
        assert 'deuda' in r['mensaje'].lower()

    @patch('services.cliente_service.ClienteModel')
    def test_eliminar_exitoso(self, mock_model):
        """Debe eliminar correctamente un cliente sin deudas."""
        mock_model.buscar_por_id.return_value       = {'id': 1, 'nombre': 'María'}
        mock_model.contar_deudas_activas.return_value = 0
        mock_model.eliminar.return_value              = 1
        r = ClienteService.eliminar(1, 1)
        assert r['exito']  == True
        assert r['codigo'] == 200


class TestActualizarCliente:
    """Pruebas para la actualización de clientes."""

    @patch('services.cliente_service.ClienteModel')
    def test_sin_campos(self, mock_model):
        """Debe rechazar actualización sin campos."""
        mock_model.buscar_por_id.return_value = {'id': 1, 'nombre': 'María'}
        r = ClienteService.actualizar(1, 1, {})
        assert r['exito']  == False
        assert r['codigo'] == 400

    @patch('services.cliente_service.ClienteModel')
    def test_actualizar_exitoso(self, mock_model):
        """Debe actualizar correctamente los campos enviados."""
        mock_model.buscar_por_id.return_value = {'id': 1, 'nombre': 'María'}
        mock_model.actualizar.return_value    = 1
        r = ClienteService.actualizar(1, 1, {'telefono': '3209999999'})
        assert r['exito']  == True
        assert r['codigo'] == 200
