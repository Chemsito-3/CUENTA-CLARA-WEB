# =============================================================================
# services/deuda_service.py - Lógica de negocio de deudas
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.deuda_model   import DeudaModel
from models.cliente_model import ClienteModel
from datetime import datetime


class DeudaService:
    """
    Servicio de gestión de deudas.
    Contiene todas las reglas de negocio relacionadas con deudas y pagos.
    """

    @staticmethod
    def _serializar_deuda(d):
        """Serializa una deuda para JSON."""
        d['total']        = float(d['total'])
        d['creado_en']    = str(d['creado_en'])
        d['fecha_limite'] = str(d['fecha_limite'])  if d['fecha_limite'] else None
        d['fecha_pago']   = str(d['fecha_pago'])    if d['fecha_pago']   else None
        return d

    @staticmethod
    def listar(tendero_id, estado=None, cliente_id=None):
        """Lista deudas con filtros y serialización."""
        cliente_id_int = int(cliente_id) if cliente_id and str(cliente_id).isdigit() else None
        deudas = DeudaModel.listar(tendero_id, estado, cliente_id_int)
        deudas = [DeudaService._serializar_deuda(d) for d in deudas]
        return {'exito': True, 'codigo': 200,
                'total': len(deudas), 'deudas': deudas}

    @staticmethod
    def obtener(deuda_id, tendero_id):
        """Obtiene detalle de deuda con productos."""
        deuda = DeudaModel.buscar_por_id(deuda_id, tendero_id)
        if not deuda:
            return {'exito': False, 'mensaje': 'Deuda no encontrada.', 'codigo': 404}

        productos = DeudaModel.obtener_productos(deuda_id)
        for p in productos:
            p['precio']   = float(p['precio'])
            p['subtotal'] = float(p['subtotal'])

        return {
            'exito'    : True, 'codigo': 200,
            'deuda'    : DeudaService._serializar_deuda(deuda),
            'productos': productos
        }

    @staticmethod
    def crear(tendero_id, cliente_id, productos, fecha_limite=None, observaciones=None):
        """
        Crea una deuda con sus productos.
        Reglas de negocio:
        - Debe tener al menos un producto
        - El cliente debe pertenecer al tendero
        - Cada producto debe tener nombre, precio > 0 y cantidad > 0
        """
        if not cliente_id:
            return {'exito': False,
                    'mensaje': 'El cliente es obligatorio.', 'codigo': 400}

        if not productos or len(productos) == 0:
            return {'exito': False,
                    'mensaje': 'Debe agregar al menos un producto.', 'codigo': 400}

        # Validar cada producto
        for i, p in enumerate(productos):
            if not p.get('nombre_producto', '').strip():
                return {'exito': False,
                        'mensaje': f'El producto #{i+1} no tiene nombre.', 'codigo': 400}
            try:
                if float(p.get('precio', 0)) <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return {'exito': False,
                        'mensaje': f'El producto #{i+1} tiene un precio inválido.',
                        'codigo': 400}
            try:
                if int(p.get('cantidad', 0)) <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return {'exito': False,
                        'mensaje': f'El producto #{i+1} tiene una cantidad inválida.',
                        'codigo': 400}

        # Verificar que el cliente pertenece al tendero
        cliente = ClienteModel.buscar_por_id(cliente_id, tendero_id)
        if not cliente:
            return {'exito': False, 'mensaje': 'Cliente no encontrado.', 'codigo': 404}

        # Crear la deuda
        deuda_id = DeudaModel.crear(
            cliente_id, tendero_id,
            fecha_limite  or None,
            observaciones or None
        )

        # Insertar productos (el trigger de MySQL actualiza el total)
        total = 0
        for p in productos:
            precio   = float(p['precio'])
            cantidad = int(p['cantidad'])
            subtotal = precio * cantidad
            total   += subtotal
            DeudaModel.agregar_producto(
                deuda_id, p['nombre_producto'].strip(),
                precio, cantidad, subtotal
            )

        return {
            'exito'   : True, 'codigo': 201,
            'mensaje' : f'Deuda registrada para "{cliente["nombre"]}".',
            'deuda_id': deuda_id,
            'total'   : total,
            'cliente' : cliente['nombre']
        }

    @staticmethod
    def agregar_producto(deuda_id, tendero_id, nombre, precio, cantidad):
        """
        Agrega un producto a deuda existente.
        Regla: solo se puede agregar a deudas pendientes o vencidas.
        """
        deuda = DeudaModel.buscar_por_id(deuda_id, tendero_id)
        if not deuda:
            return {'exito': False, 'mensaje': 'Deuda no encontrada.', 'codigo': 404}

        if deuda['estado'] == 'pagada':
            return {'exito': False,
                    'mensaje': 'No se pueden agregar productos a una deuda pagada.',
                    'codigo': 409}

        if not nombre or not nombre.strip():
            return {'exito': False,
                    'mensaje': 'El nombre del producto es obligatorio.', 'codigo': 400}

        try:
            precio   = float(precio)
            cantidad = int(cantidad)
            if precio <= 0 or cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return {'exito': False,
                    'mensaje': 'Precio y cantidad deben ser valores positivos.',
                    'codigo': 400}

        subtotal = precio * cantidad
        DeudaModel.agregar_producto(deuda_id, nombre.strip(), precio, cantidad, subtotal)

        return {'exito': True, 'codigo': 201,
                'mensaje': f'Producto "{nombre}" agregado.',
                'subtotal': subtotal}

    @staticmethod
    def pagar(deuda_id, tendero_id):
        """
        Marca la deuda como pagada.
        Regla: no se puede pagar una deuda ya pagada.
        """
        deuda = DeudaModel.buscar_por_id(deuda_id, tendero_id)
        if not deuda:
            return {'exito': False, 'mensaje': 'Deuda no encontrada.', 'codigo': 404}

        if deuda['estado'] == 'pagada':
            return {'exito': False,
                    'mensaje': 'Esta deuda ya fue pagada anteriormente.',
                    'codigo': 409}

        DeudaModel.marcar_pagada(deuda_id, tendero_id)
        return {
            'exito'      : True, 'codigo': 200,
            'mensaje'    : 'Deuda marcada como pagada exitosamente.',
            'deuda_id'   : deuda_id,
            'total_pagado': float(deuda['total']),
            'fecha_pago' : str(datetime.now())
        }

    @staticmethod
    def eliminar(deuda_id, tendero_id):
        """
        Elimina deuda.
        Regla: no se pueden eliminar deudas pagadas (son historial).
        """
        deuda = DeudaModel.buscar_por_id(deuda_id, tendero_id)
        if not deuda:
            return {'exito': False, 'mensaje': 'Deuda no encontrada.', 'codigo': 404}

        if deuda['estado'] == 'pagada':
            return {'exito': False,
                    'mensaje': 'No se puede eliminar una deuda pagada.',
                    'codigo': 409}

        DeudaModel.eliminar(deuda_id, tendero_id)
        return {'exito': True, 'codigo': 200,
                'mensaje': 'Deuda eliminada exitosamente.'}
