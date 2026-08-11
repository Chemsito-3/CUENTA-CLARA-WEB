# =============================================================================
# services/cliente_service.py - Lógica de negocio de clientes
# Proyecto: Cuenta Clara
# Evidencia: GA8-220501096-AA1-EV01 - SENA
# Autor: Carlos Varón
# =============================================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cliente_model import ClienteModel


class ClienteService:
    """
    Servicio de gestión de clientes.
    Contiene todas las reglas de negocio relacionadas con clientes.
    """

    @staticmethod
    def listar(tendero_id, buscar=None):
        """Lista clientes con serialización de tipos."""
        clientes = ClienteModel.listar(tendero_id, buscar)
        for c in clientes:
            c['creado_en']       = str(c['creado_en'])
            c['deuda_pendiente'] = float(c['deuda_pendiente'])
            c['deuda_vencida']   = float(c['deuda_vencida'])
        return {'exito': True, 'codigo': 200,
                'total': len(clientes), 'clientes': clientes}

    @staticmethod
    def obtener(cliente_id, tendero_id):
        """Obtiene detalle del cliente con resumen de deudas."""
        cliente = ClienteModel.buscar_por_id(cliente_id, tendero_id)
        if not cliente:
            return {'exito': False, 'mensaje': 'Cliente no encontrado.', 'codigo': 404}

        resumen = ClienteModel.obtener_resumen_deudas(cliente_id)
        for key in ['deuda_total', 'pendiente', 'vencida', 'pagada']:
            resumen[key] = float(resumen[key])

        # Importar aquí para evitar dependencia circular
        from models.deuda_model import DeudaModel
        deudas = DeudaModel.listar(tendero_id, cliente_id=cliente_id)
        deudas = [d for d in deudas if d['estado'] in ('pendiente', 'vencida')]
        for d in deudas:
            d['total']        = float(d['total'])
            d['creado_en']    = str(d['creado_en'])
            d['fecha_limite'] = str(d['fecha_limite']) if d['fecha_limite'] else None

        cliente['creado_en'] = str(cliente['creado_en'])
        return {
            'exito'         : True, 'codigo': 200,
            'cliente'       : cliente,
            'resumen_deudas': resumen,
            'deudas_activas': deudas
        }

    @staticmethod
    def crear(tendero_id, nombre, telefono=None, direccion=None):
        """
        Crea un cliente aplicando reglas de negocio:
        - Nombre obligatorio y mínimo 2 caracteres
        - No puede haber dos clientes con el mismo nombre en la misma tienda
        """
        nombre = nombre.strip() if nombre else ''

        if not nombre:
            return {'exito': False,
                    'mensaje': 'El nombre del cliente es obligatorio.',
                    'codigo': 400}

        if len(nombre) < 2:
            return {'exito': False,
                    'mensaje': 'El nombre debe tener al menos 2 caracteres.',
                    'codigo': 400}

        # Regla de negocio: nombre único por tienda
        if ClienteModel.buscar_por_nombre(nombre, tendero_id):
            return {'exito': False,
                    'mensaje': f'Ya tienes un cliente llamado "{nombre}".',
                    'codigo': 409}

        nuevo_id = ClienteModel.crear(
            tendero_id, nombre,
            telefono.strip()  if telefono  else None,
            direccion.strip() if direccion else None
        )

        return {
            'exito'  : True, 'codigo': 201,
            'mensaje': f'Cliente "{nombre}" creado exitosamente.',
            'cliente': {'id': nuevo_id, 'nombre': nombre,
                        'telefono': telefono, 'direccion': direccion}
        }

    @staticmethod
    def actualizar(cliente_id, tendero_id, datos):
        """Actualiza solo los campos enviados."""
        if not ClienteModel.buscar_por_id(cliente_id, tendero_id):
            return {'exito': False, 'mensaje': 'Cliente no encontrado.', 'codigo': 404}

        campos, valores = [], []
        if 'nombre' in datos and datos['nombre'].strip():
            campos.append('nombre = %s')
            valores.append(datos['nombre'].strip())
        if 'telefono' in datos:
            campos.append('telefono = %s')
            valores.append(datos['telefono'].strip() or None)
        if 'direccion' in datos:
            campos.append('direccion = %s')
            valores.append(datos['direccion'].strip() or None)

        if not campos:
            return {'exito': False,
                    'mensaje': 'No se enviaron campos para actualizar.',
                    'codigo': 400}

        ClienteModel.actualizar(cliente_id, tendero_id, campos, valores)
        return {'exito': True, 'codigo': 200,
                'mensaje': 'Cliente actualizado exitosamente.'}

    @staticmethod
    def eliminar(cliente_id, tendero_id):
        """
        Elimina lógicamente el cliente.
        Regla de negocio: no se puede eliminar si tiene deudas pendientes.
        """
        cliente = ClienteModel.buscar_por_id(cliente_id, tendero_id)
        if not cliente:
            return {'exito': False, 'mensaje': 'Cliente no encontrado.', 'codigo': 404}

        deudas_activas = ClienteModel.contar_deudas_activas(cliente_id)
        if deudas_activas > 0:
            return {
                'exito'  : False, 'codigo': 409,
                'mensaje': f'No se puede eliminar a "{cliente["nombre"]}" '
                           f'porque tiene {deudas_activas} deuda(s) pendiente(s).'
            }

        ClienteModel.eliminar(cliente_id, tendero_id)
        return {'exito': True, 'codigo': 200,
                'mensaje': f'Cliente "{cliente["nombre"]}" eliminado exitosamente.'}
