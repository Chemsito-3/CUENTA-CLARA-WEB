# =============================================================================
# routes/dashboard.py - Endpoints de resumen y alertas
# Proyecto: Cuenta Clara
# Evidencia: GA7-220501096-AA5-EV03 - SENA
# Autor: Carlos Varón
#
# Endpoints:
#   GET /api/dashboard/resumen       → Resumen general del negocio
#   GET /api/dashboard/alertas       → Deudas vencidas o por vencer
#   GET /api/dashboard/top-deudores  → Clientes que más deben
# =============================================================================

from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import execute_query
from middleware.auth_middleware import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# =============================================================================
# ENDPOINT 1: Resumen general del negocio
# =============================================================================
@dashboard_bp.route('/resumen', methods=['GET'])
@token_required
def resumen(tendero_id):
    try:
        resumen_deudas = execute_query(
            """SELECT
                   COUNT(*)                                             AS total_deudas,
                   COALESCE(SUM(total), 0)                             AS monto_total,
                   COALESCE(SUM(CASE WHEN estado = 'pendiente'
                                THEN total ELSE 0 END), 0)             AS monto_pendiente,
                   COALESCE(SUM(CASE WHEN estado = 'vencida'
                                THEN total ELSE 0 END), 0)             AS monto_vencido,
                   COALESCE(SUM(CASE WHEN estado = 'pagada'
                                THEN total ELSE 0 END), 0)             AS monto_cobrado,
                   COUNT(CASE WHEN estado = 'pendiente' THEN 1 END)    AS cant_pendientes,
                   COUNT(CASE WHEN estado = 'vencida'   THEN 1 END)    AS cant_vencidas,
                   COUNT(CASE WHEN estado = 'pagada'    THEN 1 END)    AS cant_pagadas
               FROM deudas
               WHERE tendero_id = %s""",
            (tendero_id,), fetch_one=True
        )

        total_clientes = execute_query(
            "SELECT COUNT(*) AS total FROM clientes WHERE tendero_id = %s AND activo = TRUE",
            (tendero_id,), fetch_one=True
        )

        proximas_a_vencer = execute_query(
            """SELECT COUNT(*) AS total, COALESCE(SUM(total), 0) AS monto
               FROM deudas
               WHERE tendero_id = %s
                 AND estado = 'pendiente'
                 AND fecha_limite IS NOT NULL
                 AND fecha_limite BETWEEN CURDATE()
                     AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)""",
            (tendero_id,), fetch_one=True
        )

        for key in ['monto_total', 'monto_pendiente', 'monto_vencido', 'monto_cobrado']:
            resumen_deudas[key] = float(resumen_deudas[key])

        return jsonify({
            'exito': True,
            'resumen': {
                'clientes_activos'  : total_clientes['total'],
                'deudas'            : resumen_deudas,
                'proximas_a_vencer' : {
                    'total_deudas': proximas_a_vencer['total'],
                    'monto'       : float(proximas_a_vencer['monto'])
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 2: Alertas de deudas vencidas y próximas a vencer
# =============================================================================
@dashboard_bp.route('/alertas', methods=['GET'])
@token_required
def alertas(tendero_id):
    try:
        dias = request.args.get('dias', 7)
        try:
            dias = int(dias)
            if dias < 1 or dias > 90:
                dias = 7
        except ValueError:
            dias = 7

        vencidas = execute_query(
            """SELECT d.id, d.total, d.estado, d.fecha_limite, d.observaciones,
                      c.id AS cliente_id, c.nombre AS cliente_nombre,
                      c.telefono AS cliente_telefono,
                      DATEDIFF(CURDATE(), d.fecha_limite) AS dias_vencida
               FROM deudas d
               JOIN clientes c ON c.id = d.cliente_id
               WHERE d.tendero_id = %s
                 AND d.estado IN ('pendiente', 'vencida')
                 AND d.fecha_limite IS NOT NULL
                 AND d.fecha_limite < CURDATE()
               ORDER BY d.fecha_limite ASC""",
            (tendero_id,), fetch=True
        )

        proximas = execute_query(
            """SELECT d.id, d.total, d.estado, d.fecha_limite, d.observaciones,
                      c.id AS cliente_id, c.nombre AS cliente_nombre,
                      c.telefono AS cliente_telefono,
                      DATEDIFF(d.fecha_limite, CURDATE()) AS dias_restantes
               FROM deudas d
               JOIN clientes c ON c.id = d.cliente_id
               WHERE d.tendero_id = %s
                 AND d.estado = 'pendiente'
                 AND d.fecha_limite IS NOT NULL
                 AND d.fecha_limite BETWEEN CURDATE()
                     AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
               ORDER BY d.fecha_limite ASC""",
            (tendero_id, dias), fetch=True
        )

        for d in vencidas:
            d['total']        = float(d['total'])
            d['fecha_limite'] = str(d['fecha_limite'])

        for d in proximas:
            d['total']        = float(d['total'])
            d['fecha_limite'] = str(d['fecha_limite'])

        return jsonify({
            'exito': True,
            'alertas': {
                'vencidas'          : {'total': len(vencidas),  'deudas': vencidas},
                'proximas_a_vencer' : {
                    'dias_revisados': dias,
                    'total'         : len(proximas),
                    'deudas'        : proximas
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'Error interno: {str(e)}'}), 500


# =============================================================================
# ENDPOINT 3: Top deudores
# =============================================================================
@dashboard_bp.route('/top-deudores', methods=['GET'])
@token_required
def top_deudores(tendero_id):
    try:
        limite = request.args.get('limite', 5)
        try:
            limite = int(limite)
            if limite < 1 or limite > 20:
                limite = 5
        except ValueError:
            limite = 5

        top = execute_query(
            """SELECT c.id, c.nombre, c.telefono,
                      COUNT(d.id)               AS total_deudas,
                      COALESCE(SUM(d.total), 0) AS deuda_total,
                      MAX(d.fecha_limite)        AS proxima_fecha_limite
               FROM clientes c
               JOIN deudas d ON d.cliente_id = c.id
               WHERE c.tendero_id = %s
                 AND c.activo = TRUE
                 AND d.estado IN ('pendiente', 'vencida')
               GROUP BY c.id
               ORDER BY deuda_total DESC
               LIMIT %s""",
            (tendero_id, limite), fetch=True
        )

        for t in top:
            t['deuda_total']          = float(t['deuda_total'])
            t['proxima_fecha_limite'] = str(t['proxima_fecha_limite']) \
                                        if t['proxima_fecha_limite'] else None

        return jsonify({'exito': True, 'top_deudores': top}), 200

    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'Error interno: {str(e)}'}), 500
