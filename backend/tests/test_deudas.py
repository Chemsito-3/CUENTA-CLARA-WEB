# =============================================================================
# tests/test_deudas.py - Pruebas unitarias del módulo de deudas
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch
from services.deuda_service import DeudaService

PRODUCTOS_VALIDOS = [
    {'nombre_producto': 'Arroz', 'precio': 3500, 'cantidad': 2},
    {'nombre_producto': 'Aceite', 'precio': 4200, 'cantidad': 1}
]


class TestCrearDeuda:
    """Pruebas para la creación de deudas."""

    def test_sin_cliente(self):
        """Debe rechazar deuda sin cliente."""
        r = DeudaService.crear(1, None, PRODUCTOS_VALIDOS)
        assert r['exito']  == False
        assert r['codigo'] == 400

    def test_sin_productos(self):
        """Debe rechazar deuda sin productos."""
        r = DeudaService.crear(1, 4, [])
        assert r['exito']  == False
        assert r['codigo'] == 400

    def test_producto_sin_nombre(self):
        """Debe rechazar producto sin nombre."""
        r = DeudaService.crear(1, 4, [{'nombre_producto': '', 'precio': 3000, 'cantidad': 1}])
        assert r['exito']  == False
        assert r['codigo'] == 400

    def test_producto_precio_invalido(self):
        """Debe rechazar producto con precio cero o negativo."""
        r = DeudaService.crear(1, 4, [{'nombre_producto': 'Arroz', 'precio': 0, 'cantidad': 1}])
        assert r['exito']  == False
        assert r['codigo'] == 400

    def test_producto_cantidad_invalida(self):
        """Debe rechazar producto con cantidad cero."""
        r = DeudaService.crear(1, 4, [{'nombre_producto': 'Arroz', 'precio': 3000, 'cantidad': 0}])
        assert r['exito']  == False
        assert r['codigo'] == 400

    @patch('services.deuda_service.ClienteModel')
    def test_cliente_no_encontrado(self, mock_cliente):
        """Debe retornar 404 si el cliente no pertenece al tendero."""
        mock_cliente.buscar_por_id.return_value = None
        r = DeudaService.crear(1, 99, PRODUCTOS_VALIDOS)
        assert r['exito']  == False
        assert r['codigo'] == 404

    @patch('services.deuda_service.DeudaModel')
    @patch('services.deuda_service.ClienteModel')
    def test_crear_exitoso(self, mock_cliente, mock_deuda):
        """Debe crear correctamente una deuda con productos válidos."""
        mock_cliente.buscar_por_id.return_value = {'id': 4, 'nombre': 'Pedro'}
        mock_deuda.crear.return_value           = 10
        mock_deuda.agregar_producto.return_value = 1

        r = DeudaService.crear(1, 4, PRODUCTOS_VALIDOS)
        assert r['exito']    == True
        assert r['codigo']   == 201
        assert r['deuda_id'] == 10
        assert r['total']    == 3500*2 + 4200*1  # 11200


class TestPagarDeuda:
    """Pruebas para el pago de deudas."""

    @patch('services.deuda_service.DeudaModel')
    def test_deuda_no_encontrada(self, mock_model):
        """Debe retornar 404 si la deuda no existe."""
        mock_model.buscar_por_id.return_value = None
        r = DeudaService.pagar(99, 1)
        assert r['exito']  == False
        assert r['codigo'] == 404

    @patch('services.deuda_service.DeudaModel')
    def test_deuda_ya_pagada(self, mock_model):
        """No debe permitir pagar una deuda ya pagada."""
        mock_model.buscar_por_id.return_value = {
            'id': 1, 'estado': 'pagada', 'total': 14000
        }
        r = DeudaService.pagar(1, 1)
        assert r['exito']  == False
        assert r['codigo'] == 409

    @patch('services.deuda_service.DeudaModel')
    def test_pagar_exitoso(self, mock_model):
        """Debe marcar como pagada una deuda pendiente."""
        mock_model.buscar_por_id.return_value  = {
            'id': 1, 'estado': 'pendiente', 'total': 14000
        }
        mock_model.marcar_pagada.return_value = 1
        r = DeudaService.pagar(1, 1)
        assert r['exito']        == True
        assert r['codigo']       == 200
        assert r['total_pagado'] == 14000.0


class TestEliminarDeuda:
    """Pruebas para la eliminación de deudas."""

    @patch('services.deuda_service.DeudaModel')
    def test_no_eliminar_pagada(self, mock_model):
        """No debe eliminar una deuda pagada."""
        mock_model.buscar_por_id.return_value = {'id': 1, 'estado': 'pagada', 'total': 5000}
        r = DeudaService.eliminar(1, 1)
        assert r['exito']  == False
        assert r['codigo'] == 409

    @patch('services.deuda_service.DeudaModel')
    def test_eliminar_exitoso(self, mock_model):
        """Debe eliminar correctamente una deuda pendiente."""
        mock_model.buscar_por_id.return_value = {'id': 1, 'estado': 'pendiente', 'total': 5000}
        mock_model.eliminar.return_value      = 1
        r = DeudaService.eliminar(1, 1)
        assert r['exito']  == True
        assert r['codigo'] == 200
