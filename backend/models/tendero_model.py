# =============================================================================
# models/tendero_model.py - Acceso a datos de la tabla tenderos
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
#
# PATRÓN: Repository Pattern
# Esta capa SOLO se comunica con la base de datos.
# No contiene lógica de negocio ni validaciones.
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import execute_query


class TenderoModel:
    """
    Repositorio de acceso a datos para la tabla `tenderos`.
    Cada método ejecuta una sola operación SQL.
    """

    @staticmethod
    def crear(nombre, email, contrasena_hash, nombre_tienda, telefono=None):
        """
        Inserta un nuevo tendero en la base de datos.
        Retorna el ID del registro creado.
        """
        return execute_query(
            """INSERT INTO tenderos
               (nombre, email, contrasena, nombre_tienda, telefono)
               VALUES (%s, %s, %s, %s, %s)""",
            (nombre, email, contrasena_hash, nombre_tienda, telefono)
        )

    @staticmethod
    def buscar_por_email(email):
        """
        Busca un tendero por su email.
        Retorna el registro o None si no existe.
        """
        return execute_query(
            "SELECT * FROM tenderos WHERE email = %s AND activo = TRUE",
            (email,),
            fetch_one=True
        )

    @staticmethod
    def buscar_por_credenciales(email, contrasena_hash):
        """
        Busca un tendero por email y contraseña (para autenticación).
        Retorna el registro o None si las credenciales son incorrectas.
        """
        return execute_query(
            """SELECT id, nombre, email, nombre_tienda, telefono
               FROM tenderos
               WHERE email = %s AND contrasena = %s AND activo = TRUE""",
            (email, contrasena_hash),
            fetch_one=True
        )

    @staticmethod
    def buscar_por_id(tendero_id):
        """
        Busca un tendero por su ID.
        Retorna el registro completo o None.
        """
        return execute_query(
            """SELECT id, nombre, email, nombre_tienda, telefono, creado_en
               FROM tenderos WHERE id = %s AND activo = TRUE""",
            (tendero_id,),
            fetch_one=True
        )
