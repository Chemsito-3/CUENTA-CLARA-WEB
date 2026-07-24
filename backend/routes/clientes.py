# =============================================================================
# routes/clientes.py - Endpoints de gestión de clientes
# Proyecto: Cuenta Clara
# Evidencia: GA7-220501096-AA5-EV03 - SENA
# Autor: Carlos Varón
#
# Endpoints:
#   GET    /api/clientes       → Listar todos los clientes del tendero
#   GET    /api/clientes/<id>  → Ver un cliente con su resumen de deudas
#   POST   /api/clientes       → Crear nuevo cliente
#   PUT    /api/clientes/<id>  → Actualizar datos del cliente
#   DELETE /api/clientes/<id>  → Eliminar cliente (si no tiene deudas)
# =============================================================================

from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import execute_query
from middleware.auth_middleware import token_required

clientes_bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')


# =============================================================================
# ENDPOINT 1: Listar todos los clientes del tendero
# Método:  GET
# URL:     /api/clientes
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@clientes_bp.route('/', methods=['GET'])
@token_required
def get_clientes(tendero_id):
    """
    Retorna todos los clientes activos del tendero autenticado.
    Incluye el total de deuda pendiente de cada cliente.

    Query params opcionales:
      ?buscar=nombre  → filtra clientes por nombre
    """
    try:
        buscar = request.args.get('buscar', '').strip()

        if buscar:
            # Búsqueda por nombre (LIKE para búsqueda parcial)
            clientes = execute_query(
                """SELECT
                       c.id,
                       c.nombre,
                       c.telefono,
                       c.direccion,
                       c.creado_en,
                       COUNT(d.id)                    AS total_deudas,
                       COALESCE(SUM(
                           CASE WHEN d.estado = 'pendiente'
                                THEN d.total ELSE 0 END
                       ), 0)                          AS deuda_pendiente,
                       COALESCE(SUM(
                           CASE WHEN d.estado = 'vencida'
                                THEN d.total ELSE 0 END
                       ), 0)                          AS deuda_vencida
                   FROM clientes c
                   LEFT JOIN deudas d ON d.cliente_id = c.id
                   WHERE c.tendero_id = %s
                     AND c.activo = TRUE
                     AND c.nombre LIKE %s
                   GROUP BY c.id
                   ORDER BY c.nombre ASC""",
                (tendero_id, f'%{buscar}%'),
                fetch=True
            )
        else:
            clientes = execute_query(
                """SELECT
                       c.id,
                       c.nombre,
                       c.telefono,
                       c.direccion,
                       c.creado_en,
                       COUNT(d.id)                    AS total_deudas,
                       COALESCE(SUM(
                           CASE WHEN d.estado = 'pendiente'
                                THEN d.total ELSE 0 END
                       ), 0)                          AS deuda_pendiente,
                       COALESCE(SUM(
                           CASE WHEN d.estado = 'vencida'
                                THEN d.total ELSE 0 END
                       ), 0)                          AS deuda_vencida
                   FROM clientes c
                   LEFT JOIN deudas d ON d.cliente_id = c.id
                   WHERE c.tendero_id = %s
                     AND c.activo = TRUE
                   GROUP BY c.id
                   ORDER BY c.nombre ASC""",
                (tendero_id,),
                fetch=True
            )

        # Convertir decimales y fechas a tipos serializables por JSON
        for c in clientes:
            c['creado_en']      = str(c['creado_en'])
            c['deuda_pendiente'] = float(c['deuda_pendiente'])
            c['deuda_vencida']   = float(c['deuda_vencida'])

        return jsonify({
            'exito'    : True,
            'total'    : len(clientes),
            'clientes' : clientes
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 2: Ver un cliente específico con detalle de deudas
# Método:  GET
# URL:     /api/clientes/<id>
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@token_required
def get_cliente(tendero_id, cliente_id):
    """
    Retorna los datos de un cliente específico más el resumen
    de todas sus deudas (pendientes, vencidas y pagadas).
    """
    try:
        # Verificar que el cliente pertenece a este tendero
        cliente = execute_query(
            """SELECT id, nombre, telefono, direccion, creado_en
               FROM clientes
               WHERE id = %s AND tendero_id = %s AND activo = TRUE""",
            (cliente_id, tendero_id),
            fetch_one=True
        )

        if not cliente:
            return jsonify({'exito': False,
                            'mensaje': 'Cliente no encontrado.'}), 404

        # Obtener resumen de deudas del cliente
        resumen = execute_query(
            """SELECT
                   COUNT(*)                                        AS total_deudas,
                   COALESCE(SUM(total), 0)                        AS deuda_total,
                   COALESCE(SUM(CASE WHEN estado='pendiente'
                                THEN total ELSE 0 END), 0)        AS pendiente,
                   COALESCE(SUM(CASE WHEN estado='vencida'
                                THEN total ELSE 0 END), 0)        AS vencida,
                   COALESCE(SUM(CASE WHEN estado='pagada'
                                THEN total ELSE 0 END), 0)        AS pagada
               FROM deudas
               WHERE cliente_id = %s""",
            (cliente_id,),
            fetch_one=True
        )

        # Obtener deudas pendientes y vencidas (las que importan)
        deudas_activas = execute_query(
            """SELECT id, total, estado, fecha_limite, observaciones, creado_en
               FROM deudas
               WHERE cliente_id = %s AND estado IN ('pendiente', 'vencida')
               ORDER BY creado_en DESC""",
            (cliente_id,),
            fetch=True
        )

        cliente['creado_en'] = str(cliente['creado_en'])
        for d in deudas_activas:
            d['total']      = float(d['total'])
            d['creado_en']  = str(d['creado_en'])
            d['fecha_limite'] = str(d['fecha_limite']) if d['fecha_limite'] else None

        for key in ['deuda_total', 'pendiente', 'vencida', 'pagada']:
            resumen[key] = float(resumen[key])

        return jsonify({
            'exito'        : True,
            'cliente'      : cliente,
            'resumen_deudas': resumen,
            'deudas_activas': deudas_activas
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 3: Crear nuevo cliente
# Método:  POST
# URL:     /api/clientes/
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@clientes_bp.route('/', methods=['POST'])
@token_required
def crear_cliente(tendero_id):
    """
    Crea un nuevo cliente para el tendero autenticado.

    Body JSON:
    {
        "nombre":    "María López",     (obligatorio)
        "telefono":  "3109876543",      (opcional)
        "direccion": "Calle 5 # 10-20"  (opcional)
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'exito': False,
                        'mensaje': 'No se recibieron datos.'}), 400

    nombre = data.get('nombre', '').strip()
    if not nombre:
        return jsonify({'exito': False,
                        'mensaje': 'El nombre del cliente es obligatorio.'}), 400

    if len(nombre) < 2:
        return jsonify({'exito': False,
                        'mensaje': 'El nombre debe tener al menos 2 caracteres.'}), 400

    telefono  = data.get('telefono', '').strip()
    direccion = data.get('direccion', '').strip()

    try:
        # Verificar que no exista ya un cliente con ese nombre para este tendero
        existente = execute_query(
            """SELECT id FROM clientes
               WHERE tendero_id = %s AND nombre = %s AND activo = TRUE""",
            (tendero_id, nombre),
            fetch_one=True
        )
        if existente:
            return jsonify({'exito': False,
                            'mensaje': f'Ya tienes un cliente llamado "{nombre}".'}), 409

        nuevo_id = execute_query(
            """INSERT INTO clientes (tendero_id, nombre, telefono, direccion)
               VALUES (%s, %s, %s, %s)""",
            (tendero_id, nombre, telefono or None, direccion or None)
        )

        return jsonify({
            'exito'  : True,
            'mensaje': f'Cliente "{nombre}" creado exitosamente.',
            'cliente': {
                'id'       : nuevo_id,
                'nombre'   : nombre,
                'telefono' : telefono,
                'direccion': direccion
            }
        }), 201

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 4: Actualizar datos de un cliente
# Método:  PUT
# URL:     /api/clientes/<id>
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@token_required
def actualizar_cliente(tendero_id, cliente_id):
    """
    Actualiza los datos de un cliente existente.

    Body JSON (todos opcionales, solo envía lo que quieres cambiar):
    {
        "nombre":    "María López Rodríguez",
        "telefono":  "3209876543",
        "direccion": "Carrera 10 # 5-30"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'exito': False,
                        'mensaje': 'No se recibieron datos.'}), 400

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

        # Construir actualización dinámica (solo los campos enviados)
        campos = []
        valores = []

        if 'nombre' in data and data['nombre'].strip():
            campos.append('nombre = %s')
            valores.append(data['nombre'].strip())

        if 'telefono' in data:
            campos.append('telefono = %s')
            valores.append(data['telefono'].strip() or None)

        if 'direccion' in data:
            campos.append('direccion = %s')
            valores.append(data['direccion'].strip() or None)

        if not campos:
            return jsonify({'exito': False,
                            'mensaje': 'No se enviaron campos para actualizar.'}), 400

        valores.extend([cliente_id, tendero_id])
        execute_query(
            f"UPDATE clientes SET {', '.join(campos)} WHERE id = %s AND tendero_id = %s",
            tuple(valores)
        )

        return jsonify({
            'exito'  : True,
            'mensaje': f'Cliente actualizado exitosamente.'
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 5: Eliminar un cliente
# Método:  DELETE
# URL:     /api/clientes/<id>
# Acceso:  Privado (requiere token JWT)
# =============================================================================
@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@token_required
def eliminar_cliente(tendero_id, cliente_id):
    """
    Elimina un cliente de forma segura.
    Si tiene deudas pendientes, no se puede eliminar.
    Si no tiene deudas activas, se hace una eliminación lógica (activo=FALSE).
    """
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

        # Verificar si tiene deudas pendientes o vencidas
        deudas_activas = execute_query(
            """SELECT COUNT(*) AS total FROM deudas
               WHERE cliente_id = %s AND estado IN ('pendiente', 'vencida')""",
            (cliente_id,),
            fetch_one=True
        )

        if deudas_activas['total'] > 0:
            return jsonify({
                'exito'  : False,
                'mensaje': f'No se puede eliminar a "{cliente["nombre"]}" porque '
                           f'tiene {deudas_activas["total"]} deuda(s) pendiente(s).'
            }), 409

        # Eliminación lógica: marcamos como inactivo, no borramos de la BD
        execute_query(
            "UPDATE clientes SET activo = FALSE WHERE id = %s AND tendero_id = %s",
            (cliente_id, tendero_id)
        )

        return jsonify({
            'exito'  : True,
            'mensaje': f'Cliente "{cliente["nombre"]}" eliminado exitosamente.'
        }), 200

    except Exception as e:
        return jsonify({'exito': False,
                        'mensaje': f'Error interno: {str(e)}'}), 500
