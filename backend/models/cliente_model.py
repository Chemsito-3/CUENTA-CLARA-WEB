# =============================================================================
# models/cliente_model.py - Acceso a datos de la tabla clientes
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import execute_query


class ClienteModel:
    """
    Repositorio de acceso a datos para la tabla `clientes`.
    """

    @staticmethod
    def listar(tendero_id, buscar=None):
        """
        Lista todos los clientes activos del tendero.
        Si buscar está definido, filtra por nombre.
        Incluye resumen de deudas de cada cliente.
        """
        base_query = """
            SELECT
                c.id, c.nombre, c.telefono, c.direccion, c.creado_en,
                COUNT(d.id)                                        AS total_deudas,
                COALESCE(SUM(CASE WHEN d.estado='pendiente'
                            THEN d.total ELSE 0 END), 0)          AS deuda_pendiente,
                COALESCE(SUM(CASE WHEN d.estado='vencida'
                            THEN d.total ELSE 0 END), 0)          AS deuda_vencida
            FROM clientes c
            LEFT JOIN deudas d ON d.cliente_id = c.id
            WHERE c.tendero_id = %s AND c.activo = TRUE
        """
        if buscar:
            base_query += " AND c.nombre LIKE %s GROUP BY c.id ORDER BY c.nombre"
            return execute_query(base_query, (tendero_id, f'%{buscar}%'), fetch=True)
        base_query += " GROUP BY c.id ORDER BY c.nombre"
        return execute_query(base_query, (tendero_id,), fetch=True)

    @staticmethod
    def buscar_por_id(cliente_id, tendero_id):
        """
        Busca un cliente específico verificando que pertenezca al tendero.
        """
        return execute_query(
            """SELECT id, nombre, telefono, direccion, creado_en
               FROM clientes
               WHERE id = %s AND tendero_id = %s AND activo = TRUE""",
            (cliente_id, tendero_id),
            fetch_one=True
        )

    @staticmethod
    def buscar_por_nombre(nombre, tendero_id):
        """
        Busca un cliente por nombre exacto para verificar duplicados.
        """
        return execute_query(
            """SELECT id FROM clientes
               WHERE tendero_id = %s AND nombre = %s AND activo = TRUE""",
            (tendero_id, nombre),
            fetch_one=True
        )

    @staticmethod
    def crear(tendero_id, nombre, telefono=None, direccion=None):
        """Inserta un nuevo cliente. Retorna el ID creado."""
        return execute_query(
            """INSERT INTO clientes (tendero_id, nombre, telefono, direccion)
               VALUES (%s, %s, %s, %s)""",
            (tendero_id, nombre, telefono, direccion)
        )

    @staticmethod
    def actualizar(cliente_id, tendero_id, campos, valores):
        """
        Actualiza dinámicamente los campos enviados.
        campos: lista de strings  ej: ['nombre = %s', 'telefono = %s']
        valores: tupla con los valores correspondientes
        """
        return execute_query(
            f"UPDATE clientes SET {', '.join(campos)} WHERE id = %s AND tendero_id = %s",
            tuple(valores) + (cliente_id, tendero_id)
        )

    @staticmethod
    def eliminar(cliente_id, tendero_id):
        """Eliminación lógica — marca activo = FALSE."""
        return execute_query(
            "UPDATE clientes SET activo = FALSE WHERE id = %s AND tendero_id = %s",
            (cliente_id, tendero_id)
        )

    @staticmethod
    def contar_deudas_activas(cliente_id):
        """
        Cuenta las deudas pendientes o vencidas de un cliente.
        Usado antes de eliminar para evitar inconsistencias.
        """
        resultado = execute_query(
            """SELECT COUNT(*) AS total FROM deudas
               WHERE cliente_id = %s AND estado IN ('pendiente', 'vencida')""",
            (cliente_id,),
            fetch_one=True
        )
        return resultado['total'] if resultado else 0

    @staticmethod
    def obtener_resumen_deudas(cliente_id):
        """Obtiene el resumen financiero de un cliente."""
        return execute_query(
            """SELECT
                   COUNT(*)                                      AS total_deudas,
                   COALESCE(SUM(total), 0)                       AS deuda_total,
                   COALESCE(SUM(CASE WHEN estado='pendiente'
                                THEN total ELSE 0 END), 0)       AS pendiente,
                   COALESCE(SUM(CASE WHEN estado='vencida'
                                THEN total ELSE 0 END), 0)       AS vencida,
                   COALESCE(SUM(CASE WHEN estado='pagada'
                                THEN total ELSE 0 END), 0)       AS pagada
               FROM deudas WHERE cliente_id = %s""",
            (cliente_id,),
            fetch_one=True
        )
