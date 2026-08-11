# =============================================================================
# config.py - Configuración central del proyecto
# Proyecto: Cuenta Clara
# Evidencia: GA7-220501096-AA5-EV03 - SENA
# =============================================================================

import os

class Config:
    """
    Clase de configuración central.
    Agrupa todas las variables que pueden cambiar entre entornos
    (desarrollo, producción, testing).
    """

    # ── Base de datos ──────────────────────────────────────────────────────────
    # Modifica estos valores según tu entorno local
    DB_HOST     = 'localhost'
    DB_PORT     = 3306           # Cambia a 3307 si tu MySQL usa ese puerto
    DB_NAME     = 'cuenta_clara'
    DB_USER     = 'root'
    DB_PASSWORD = 'Michi333'             # ← Pon aquí tu contraseña de MySQL

    # ── JWT (JSON Web Tokens) ──────────────────────────────────────────────────
    # Clave secreta para firmar los tokens de autenticación.
    # En producción debe ser una cadena larga y aleatoria, NUNCA hardcodeada.
    JWT_SECRET  = 'cuenta_clara_secret_key_2024'
    JWT_EXPIRATION_HOURS = 24    # El token dura 24 horas

    # ── Aplicación ─────────────────────────────────────────────────────────────
    DEBUG = True                 # False en producción
    PORT  = 5000
