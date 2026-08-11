# =============================================================================
# services/dashboard_service.py - Lógica de negocio del dashboard
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.deuda_model   import DeudaModel
from models.cliente_model import ClienteModel


class DashboardService:
    """
    Servicio del dashboard.
    Agrega datos de múltiples modelos para generar métricas del negocio.
    """

    @staticmethod
    def obtener_resumen(tendero_id):
        """Genera el resumen completo del negocio."""
        resumen = DeudaModel.obtener_resumen(tendero_id)
        for key in ['monto_total','monto_pendiente','monto_vencido','monto_cobrado']:
            resumen[key] = float(resumen[key])

        clientes = ClienteModel.listar(tendero_id)
        proximas = DeudaModel.obtener_proximas_a_vencer_resumen(tendero_id)

        return {
            'exito': True, 'codigo': 200,
            'resumen': {
                'clientes_activos' : len(clientes),
                'deudas'           : resumen,
                'proximas_a_vencer': {
                    'total_deudas': proximas['total'],
                    'monto'       : float(proximas['monto'])
                }
            }
        }

    @staticmethod
    def obtener_alertas(tendero_id, dias=7):
        """Genera alertas de deudas vencidas y próximas a vencer."""
        try:
            dias = int(dias)
            if dias < 1 or dias > 90:
                dias = 7
        except (ValueError, TypeError):
            dias = 7

        vencidas = DeudaModel.obtener_vencidas(tendero_id)
        proximas = DeudaModel.obtener_proximas(tendero_id, dias)

        for d in vencidas:
            d['total']        = float(d['total'])
            d['fecha_limite'] = str(d['fecha_limite'])

        for d in proximas:
            d['total']        = float(d['total'])
            d['fecha_limite'] = str(d['fecha_limite'])

        return {
            'exito': True, 'codigo': 200,
            'alertas': {
                'vencidas'          : {'total': len(vencidas), 'deudas': vencidas},
                'proximas_a_vencer' : {
                    'dias_revisados': dias,
                    'total'         : len(proximas),
                    'deudas'        : proximas
                }
            }
        }

    @staticmethod
    def obtener_top_deudores(tendero_id, limite=5):
        """Lista los clientes con mayor deuda pendiente."""
        try:
            limite = int(limite)
            if limite < 1 or limite > 20:
                limite = 5
        except (ValueError, TypeError):
            limite = 5

        top = DeudaModel.obtener_top_deudores(tendero_id, limite)
        for t in top:
            t['deuda_total']          = float(t['deuda_total'])
            t['proxima_fecha_limite'] = str(t['proxima_fecha_limite']) \
                                        if t['proxima_fecha_limite'] else None

        return {'exito': True, 'codigo': 200, 'top_deudores': top}
