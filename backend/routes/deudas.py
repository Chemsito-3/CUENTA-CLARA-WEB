# =============================================================================
# routes/deudas.py - Endpoints de gestión de deudas y pagos
# Proyecto: Cuenta Clara
# Evidencia: GA7-220501096-AA5-EV03 - SENA
# Autor: Carlos Varón
#
# Endpoints:
#   GET    /api/deudas                  → Listar deudas con filtros
#   GET    /api/deudas/<id>             → Ver deuda con sus productos
#   POST   /api/deudas                  → Registrar nueva deuda
#   POST   /api/deudas/<id>/productos   → Agregar producto a deuda existente
#   PATCH  /api/deudas/<id>/pagar       → Marcar deuda como pagada
#   DELETE /api/deudas/<id>             → Eliminar deuda pendiente
# =============================================================================

from flask import Blueprint, request, jsonify
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import execute_query
from middleware.auth_middleware import token_required

deudas_bp = Blueprint('deudas', __name__, url_prefix='/api/deudas')


# =============================================================================
# ENDPOINT 1: Listar deudas del tendero con filtros
# Método:  GET
# URL:     /api/deudas
# Acceso:  Privado (requiere token JWT)
#
# Query params opcionales:
#   ?estado=pendiente|pagada|vencida  → filtrar por estado
#   ?cliente_id=1                     → filtrar por cliente
# =============================================================================
@deudas_bp.route('/', methods=['GET'])
@token_required
def get_deudas(tendero_id):
    """
    Lista todas las deudas del tendero con información del cliente.
    Permite filtrar por estado y por cliente.
    """
    try:
        estado     = request.args.get('estado', '').strip()
        cliente_id = request.args.get('cliente_id', '').strip()

        # Construir query dinámicamente según los filtros recibidos
        query  = """
            SELECT
                d.id,
                d.total,
                d.estado,
                d.fecha_limite,
                d.fecha_pago,
                d.observaciones,
                d.creado_en,
                c.id        AS cliente_id,
                c.nombre    AS cliente_nombre,
                c.telefono  AS cliente_telefono,
                COUNT(dd.id) AS cantidad_productos
            FROM deudas d
            JOIN clientes c ON c.id = d.cliente_id
            LEFT JOIN detalle_deuda dd ON dd.deuda_id = d.id
            WHERE d.tendero_id = %s
        """
        params = [tendero_id]

        if estado in ('pendiente', 'pagada', 'vencida'):
            query  += " AND d.estado = %s"
            params.append(estado)

        if cliente_id.isdigit():
            query  += " AND d.cliente_id = %s"
            params.append(int(cliente_id))

        query += " GROUP BY d.id ORDER BY d.creado_en DESC"

        deudas = execute_query(query, tuple(params), fetch=True)

        # Serializar tipos no compatibles con JSON
        for d in deudas:
            d['total']        = float(d['total'])
            d['creado_en']    = str(d['creado_en'])
            d['fecha_limite'] = str(d['fecha_limite'])  if d['fecha_limite'] else None
            d['fecha_pago']   = str(d['fecha_pago'])    if d['fecha_pago']   else None

        return jsonify({
            'exito' : True,
            'total' : len(deudas),
            'deudas': deudas
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 2: Ver detalle de una deuda con sus productos
# Método:  GET
# URL:     /api/deudas/<id>
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@deudas_bp.route('/<int:deuda_id>', methods=['GET'])
@token_required
def get_deuda(tendero_id, deuda_id):
    """
    Retorna el detalle completo de una deuda:
    - Datos de la deuda
    - Datos del cliente
    - Lista de productos (detalle_deuda)
    """
    try:
        deuda = execute_query(
            """SELECT
                   d.id, d.total, d.estado, d.fecha_limite,
                   d.fecha_pago, d.observaciones, d.creado_en,
                   c.id       AS cliente_id,
                   c.nombre   AS cliente_nombre,
                   c.telefono AS cliente_telefono
               FROM deudas d
               JOIN clientes c ON c.id = d.cliente_id
               WHERE d.id = %s AND d.tendero_id = %s""",
            (deuda_id, tendero_id),
            fetch_one=True
        )

        if not deuda:
            return jsonify({'exito': False,
                            'mensaje': 'Deuda no encontrada.'}), 404

        # Obtener los productos de esta deuda
        productos = execute_query(
            """SELECT id, nombre_producto, precio, cantidad, subtotal
               FROM detalle_deuda
               WHERE deuda_id = %s
               ORDER BY id ASC""",
            (deuda_id,),
            fetch=True
        )

        # Serializar
        deuda['total']        = float(deuda['total'])
        deuda['creado_en']    = str(deuda['creado_en'])
        deuda['fecha_limite'] = str(deuda['fecha_limite']) if deuda['fecha_limite'] else None
        deuda['fecha_pago']   = str(deuda['fecha_pago'])   if deuda['fecha_pago']   else None

        for p in productos:
            p['precio']   = float(p['precio'])
            p['subtotal'] = float(p['subtotal'])

        return jsonify({
            'exito'    : True,
            'deuda'    : deuda,
            'productos': productos
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 3: Registrar nueva deuda con productos
# Método:  POST
# URL:     /api/deudas
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@deudas_bp.route('/', methods=['POST'])
@token_required
def crear_deuda(tendero_id):
    """
    Registra una nueva deuda para un cliente con sus productos.

    Body JSON:
    {
        "cliente_id":   4,
        "fecha_limite": "2024-12-31",       (opcional)
        "observaciones": "Paga los viernes", (opcional)
        "productos": [
            {
                "nombre_producto": "Arroz x 500g",
                "precio":   3500,
                "cantidad": 2
            },
            {
                "nombre_producto": "Aceite 250ml",
                "precio":   4200,
                "cantidad": 1
            }
        ]
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'exito': False,
                        'mensaje': 'No se recibieron datos.'}), 400

    cliente_id = data.get('cliente_id')
    productos  = data.get('productos', [])

    # Validaciones
    if not cliente_id:
        return jsonify({'exito': False,
                        'mensaje': 'El campo "cliente_id" es obligatorio.'}), 400

    if not productos or len(productos) == 0:
        return jsonify({'exito': False,
                        'mensaje': 'Debe agregar al menos un producto a la deuda.'}), 400

    # Validar cada producto
    for i, p in enumerate(productos):
        if not p.get('nombre_producto', '').strip():
            return jsonify({'exito': False,
                            'mensaje': f'El producto #{i+1} no tiene nombre.'}), 400
        if not p.get('precio') or float(p['precio']) <= 0:
            return jsonify({'exito': False,
                            'mensaje': f'El producto #{i+1} tiene un precio inválido.'}), 400
        if not p.get('cantidad') or int(p['cantidad']) <= 0:
            return jsonify({'exito': False,
                            'mensaje': f'El producto #{i+1} tiene una cantidad inválida.'}), 400

    try:
        # Verificar que el cliente pertenece a este tendero
        cliente = execute_query(
            """SELECT id, nombre FROM clientes
               WHERE id = %s AND tendero_id = %s AND activo = TRUE""",
            (cliente_id, tendero_id),
            fetch_one=True
        )
        if not cliente:
            return jsonify({'exito': False,
                            'mensaje': 'Cliente no encontrado.'}), 404

        fecha_limite  = data.get('fecha_limite')
        observaciones = data.get('observaciones', '').strip()

        # Crear la deuda principal
        deuda_id = execute_query(
            """INSERT INTO deudas (cliente_id, tendero_id, fecha_limite, observaciones)
               VALUES (%s, %s, %s, %s)""",
            (cliente_id, tendero_id,
             fecha_limite or None,
             observaciones or None)
        )

        # Insertar cada producto — el trigger actualizará el total automáticamente
        total = 0
        for p in productos:
            nombre   = p['nombre_producto'].strip()
            precio   = float(p['precio'])
            cantidad = int(p['cantidad'])
            subtotal = precio * cantidad
            total   += subtotal

            execute_query(
                """INSERT INTO detalle_deuda
                   (deuda_id, nombre_producto, precio, cantidad, subtotal)
                   VALUES (%s, %s, %s, %s, %s)""",
                (deuda_id, nombre, precio, cantidad, subtotal)
            )

        return jsonify({
            'exito'   : True,
            'mensaje' : f'Deuda registrada para "{cliente["nombre"]}".',
            'deuda_id': deuda_id,
            'total'   : total,
            'cliente' : cliente['nombre']
        }), 201

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 4: Agregar producto a deuda existente
# Método:  POST
# URL:     /api/deudas/<id>/productos
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@deudas_bp.route('/<int:deuda_id>/productos', methods=['POST'])
@token_required
def agregar_producto(tendero_id, deuda_id):
    """
    Agrega un producto adicional a una deuda que ya existe.
    Solo funciona si la deuda está en estado 'pendiente'.

    Body JSON:
    {
        "nombre_producto": "Gaseosa 1.5L",
        "precio":   5000,
        "cantidad": 2
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'exito': False,
                        'mensaje': 'No se recibieron datos.'}), 400

    nombre   = data.get('nombre_producto', '').strip()
    precio   = data.get('precio')
    cantidad = data.get('cantidad', 1)

    if not nombre:
        return jsonify({'exito': False,
                        'mensaje': 'El nombre del producto es obligatorio.'}), 400
    if not precio or float(precio) <= 0:
        return jsonify({'exito': False,
                        'mensaje': 'El precio debe ser mayor a 0.'}), 400

    try:
        # Verificar que la deuda pertenece a este tendero y está pendiente
        deuda = execute_query(
            """SELECT id, estado FROM deudas
               WHERE id = %s AND tendero_id = %s""",
            (deuda_id, tendero_id),
            fetch_one=True
        )

        if not deuda:
            return jsonify({'exito': False,
                            'mensaje': 'Deuda no encontrada.'}), 404

        if deuda['estado'] == 'pagada':
            return jsonify({'exito': False,
                            'mensaje': 'No se pueden agregar productos a una deuda ya pagada.'}), 409

        precio   = float(precio)
        cantidad = int(cantidad)
        subtotal = precio * cantidad

        execute_query(
            """INSERT INTO detalle_deuda
               (deuda_id, nombre_producto, precio, cantidad, subtotal)
               VALUES (%s, %s, %s, %s, %s)""",
            (deuda_id, nombre, precio, cantidad, subtotal)
        )

        return jsonify({
            'exito'   : True,
            'mensaje' : f'Producto "{nombre}" agregado a la deuda.',
            'subtotal': subtotal
        }), 201

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 5: Marcar deuda como pagada
# Método:  PATCH
# URL:     /api/deudas/<id>/pagar
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@deudas_bp.route('/<int:deuda_id>/pagar', methods=['PATCH'])
@token_required
def pagar_deuda(tendero_id, deuda_id):
    """
    Marca una deuda como pagada y registra la fecha y hora del pago.
    Solo se puede pagar una deuda que esté pendiente o vencida.
    """
    try:
        deuda = execute_query(
            """SELECT id, estado, total FROM deudas
               WHERE id = %s AND tendero_id = %s""",
            (deuda_id, tendero_id),
            fetch_one=True
        )

        if not deuda:
            return jsonify({'exito': False,
                            'mensaje': 'Deuda no encontrada.'}), 404

        if deuda['estado'] == 'pagada':
            return jsonify({'exito': False,
                            'mensaje': 'Esta deuda ya fue pagada anteriormente.'}), 409

        # Registrar el pago con fecha y hora exacta
        execute_query(
            """UPDATE deudas
               SET estado = 'pagada', fecha_pago = %s
               WHERE id = %s AND tendero_id = %s""",
            (datetime.now(), deuda_id, tendero_id)
        )

        return jsonify({
            'exito'     : True,
            'mensaje'   : f'Deuda marcada como pagada exitosamente.',
            'deuda_id'  : deuda_id,
            'total_pagado': float(deuda['total']),
            'fecha_pago': str(datetime.now())
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 6: Eliminar deuda
# Método:  DELETE
# URL:     /api/deudas/<id>
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@deudas_bp.route('/<int:deuda_id>', methods=['DELETE'])
@token_required
def eliminar_deuda(tendero_id, deuda_id):
    """
    Elimina una deuda y todos sus productos.
    Solo se pueden eliminar deudas en estado 'pendiente'.
    Las deudas pagadas no se pueden eliminar (son historial).
    """
    try:
        deuda = execute_query(
            """SELECT id, estado, total FROM deudas
               WHERE id = %s AND tendero_id = %s""",
            (deuda_id, tendero_id),
            fetch_one=True
        )

        if not deuda:
            return jsonify({'exito': False,
                            'mensaje': 'Deuda no encontrada.'}), 404

        if deuda['estado'] == 'pagada':
            return jsonify({'exito': False,
                            'mensaje': 'No se puede eliminar una deuda ya pagada.'}), 409

        # El CASCADE en la BD elimina automáticamente los productos (detalle_deuda)
        execute_query(
            "DELETE FROM deudas WHERE id = %s AND tendero_id = %s",
            (deuda_id, tendero_id)
        )

        return jsonify({
            'exito'  : True,
            'mensaje': f'Deuda eliminada exitosamente.'
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500
