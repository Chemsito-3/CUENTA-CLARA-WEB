# =============================================================================
# database.py - Utilidad de conexión a MySQL
# Proyecto: Cuenta Clara
# =============================================================================

import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    """
    Crea y retorna una conexión a la base de datos MySQL.
    Usa la configuración definida en config.py.
    """
    try:
        connection = mysql.connector.connect(
            host     = Config.DB_HOST,
            port     = Config.DB_PORT,
            database = Config.DB_NAME,
            user     = Config.DB_USER,
            password = Config.DB_PASSWORD
        )
        return connection
    except Error as e:
        raise Exception(f"Error de conexión a MySQL: {e}")


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    Ejecuta una consulta SQL de forma segura.

    Args:
        query     (str):   Consulta SQL con placeholders %s.
        params    (tuple): Valores para los placeholders.
        fetch     (bool):  True para SELECT que retorna múltiples filas.
        fetch_one (bool):  True para SELECT que retorna una sola fila.

    Returns:
        - Lista de diccionarios si fetch=True
        - Diccionario si fetch_one=True
        - lastrowid (int) si es INSERT
        - rowcount (int) si es UPDATE/DELETE
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
        elif fetch_one:
            result = cursor.fetchone()
        else:
            conn.commit()
            result = cursor.lastrowid if cursor.lastrowid else cursor.rowcount

        return result

    except Error as e:
        conn.rollback()
        raise Exception(f"Error en consulta SQL: {e}")
    finally:
        cursor.close()
        conn.close()
