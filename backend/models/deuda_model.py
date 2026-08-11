# =============================================================================
# models/deuda_model.py - Acceso a datos de las tablas deudas y detalle_deuda
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import execute_query
from datetime import datetime


class DeudaModel:
    """
    Repositorio de acceso a datos para las tablas `deudas` y `detalle_deuda`.
    """

    @staticmethod
    def listar(tendero_id, estado=None, cliente_id=None):
        """Lista deudas con filtros opcionales por estado y cliente."""
        query = """
            SELECT d.id, d.total, d.estado, d.fecha_limite,
                   d.fecha_pago, d.observaciones, d.creado_en,
                   c.id AS cliente_id, c.nombre AS cliente_nombre,
                   c.telefono AS cliente_telefono,
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

        if cliente_id:
            query  += " AND d.cliente_id = %s"
            params.append(cliente_id)

        query += " GROUP BY d.id ORDER BY d.creado_en DESC"
        return execute_query(query, tuple(params), fetch=True)

    @staticmethod
    def buscar_por_id(deuda_id, tendero_id):
        """Busca una deuda verificando que pertenezca al tendero."""
        return execute_query(
            """SELECT d.id, d.total, d.estado, d.fecha_limite,
                      d.fecha_pago, d.observaciones, d.creado_en,
                      c.id AS cliente_id, c.nombre AS cliente_nombre,
                      c.telefono AS cliente_telefono
               FROM deudas d
               JOIN clientes c ON c.id = d.cliente_id
               WHERE d.id = %s AND d.tendero_id = %s""",
            (deuda_id, tendero_id),
            fetch_one=True
        )

    @staticmethod
    def crear(cliente_id, tendero_id, fecha_limite=None, observaciones=None):
        """Crea una nueva deuda. Retorna el ID creado."""
        return execute_query(
            """INSERT INTO deudas (cliente_id, tendero_id, fecha_limite, observaciones)
               VALUES (%s, %s, %s, %s)""",
            (cliente_id, tendero_id, fecha_limite, observaciones)
        )

    @staticmethod
    def agregar_producto(deuda_id, nombre, precio, cantidad, subtotal):
        """Agrega un producto al detalle de la deuda."""
        return execute_query(
            """INSERT INTO detalle_deuda
               (deuda_id, nombre_producto, precio, cantidad, subtotal)
               VALUES (%s, %s, %s, %s, %s)""",
            (deuda_id, nombre, precio, cantidad, subtotal)
        )

    @staticmethod
    def obtener_productos(deuda_id):
        """Obtiene todos los productos de una deuda."""
        return execute_query(
            """SELECT id, nombre_producto, precio, cantidad, subtotal
               FROM detalle_deuda WHERE deuda_id = %s ORDER BY id""",
            (deuda_id,),
            fetch=True
        )

    @staticmethod
    def marcar_pagada(deuda_id, tendero_id):
        """Actualiza el estado a pagada con fecha y hora exacta."""
        return execute_query(
            """UPDATE deudas SET estado='pagada', fecha_pago=%s
               WHERE id = %s AND tendero_id = %s""",
            (datetime.now(), deuda_id, tendero_id)
        )

    @staticmethod
    def eliminar(deuda_id, tendero_id):
        """Elimina una deuda (el CASCADE elimina sus productos)."""
        return execute_query(
            "DELETE FROM deudas WHERE id = %s AND tendero_id = %s",
            (deuda_id, tendero_id)
        )

    @staticmethod
    def obtener_resumen(tendero_id):
        """Obtiene métricas generales de deudas para el dashboard."""
        return execute_query(
            """SELECT
                   COUNT(*)                                          AS total_deudas,
                   COALESCE(SUM(total), 0)                           AS monto_total,
                   COALESCE(SUM(CASE WHEN estado='pendiente'
                                THEN total ELSE 0 END), 0)           AS monto_pendiente,
                   COALESCE(SUM(CASE WHEN estado='vencida'
                                THEN total ELSE 0 END), 0)           AS monto_vencido,
                   COALESCE(SUM(CASE WHEN estado='pagada'
                                THEN total ELSE 0 END), 0)           AS monto_cobrado,
                   COUNT(CASE WHEN estado='pendiente' THEN 1 END)    AS cant_pendientes,
                   COUNT(CASE WHEN estado='vencida'   THEN 1 END)    AS cant_vencidas,
                   COUNT(CASE WHEN estado='pagada'    THEN 1 END)    AS cant_pagadas
               FROM deudas WHERE tendero_id = %s""",
            (tendero_id,),
            fetch_one=True
        )

    @staticmethod
    def obtener_vencidas(tendero_id):
        """Obtiene deudas ya vencidas para alertas."""
        return execute_query(
            """SELECT d.id, d.total, d.estado, d.fecha_limite, d.observaciones,
                      c.id AS cliente_id, c.nombre AS cliente_nombre,
                      c.telefono AS cliente_telefono,
                      DATEDIFF(CURDATE(), d.fecha_limite) AS dias_vencida
               FROM deudas d JOIN clientes c ON c.id = d.cliente_id
               WHERE d.tendero_id = %s AND d.estado IN ('pendiente','vencida')
                 AND d.fecha_limite IS NOT NULL AND d.fecha_limite < CURDATE()
               ORDER BY d.fecha_limite ASC""",
            (tendero_id,),
            fetch=True
        )

    @staticmethod
    def obtener_proximas(tendero_id, dias):
        """Obtiene deudas próximas a vencer en los próximos N días."""
        return execute_query(
            """SELECT d.id, d.total, d.estado, d.fecha_limite, d.observaciones,
                      c.id AS cliente_id, c.nombre AS cliente_nombre,
                      c.telefono AS cliente_telefono,
                      DATEDIFF(d.fecha_limite, CURDATE()) AS dias_restantes
               FROM deudas d JOIN clientes c ON c.id = d.cliente_id
               WHERE d.tendero_id = %s AND d.estado = 'pendiente'
                 AND d.fecha_limite IS NOT NULL
                 AND d.fecha_limite BETWEEN CURDATE()
                     AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
               ORDER BY d.fecha_limite ASC""",
            (tendero_id, dias),
            fetch=True
        )

    @staticmethod
    def obtener_top_deudores(tendero_id, limite):
        """Obtiene los clientes con mayor deuda pendiente."""
        return execute_query(
            """SELECT c.id, c.nombre, c.telefono,
                      COUNT(d.id) AS total_deudas,
                      COALESCE(SUM(d.total), 0) AS deuda_total,
                      MAX(d.fecha_limite) AS proxima_fecha_limite
               FROM clientes c JOIN deudas d ON d.cliente_id = c.id
               WHERE c.tendero_id = %s AND c.activo = TRUE
                 AND d.estado IN ('pendiente','vencida')
               GROUP BY c.id ORDER BY deuda_total DESC LIMIT %s""",
            (tendero_id, limite),
            fetch=True
        )

    @staticmethod
    def obtener_proximas_a_vencer_resumen(tendero_id):
        """Resumen de deudas que vencen en los próximos 7 días."""
        return execute_query(
            """SELECT COUNT(*) AS total, COALESCE(SUM(total), 0) AS monto
               FROM deudas
               WHERE tendero_id = %s AND estado = 'pendiente'
                 AND fecha_limite IS NOT NULL
                 AND fecha_limite BETWEEN CURDATE()
                     AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)""",
            (tendero_id,),
            fetch_one=True
        )
