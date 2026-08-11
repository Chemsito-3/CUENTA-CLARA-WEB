# routes/deudas.py - Capa de presentación: deudas
from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.deuda_service    import DeudaService
from middleware.auth_middleware import token_required

deudas_bp = Blueprint('deudas', __name__, url_prefix='/api/deudas')

@deudas_bp.route('/', methods=['GET'])
@token_required
def get_deudas(tendero_id):
    r = DeudaService.listar(tendero_id,
        request.args.get('estado','').strip() or None,
        request.args.get('cliente_id','').strip() or None)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@deudas_bp.route('/<int:deuda_id>', methods=['GET'])
@token_required
def get_deuda(tendero_id, deuda_id):
    r = DeudaService.obtener(deuda_id, tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@deudas_bp.route('/', methods=['POST'])
@token_required
def crear_deuda(tendero_id):
    data = request.get_json()
    if not data:
        return jsonify({'exito': False, 'mensaje': 'No se recibieron datos.'}), 400
    r = DeudaService.crear(tendero_id, data.get('cliente_id'),
        data.get('productos',[]), data.get('fecha_limite'),
        data.get('observaciones',''))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@deudas_bp.route('/<int:deuda_id>/productos', methods=['POST'])
@token_required
def agregar_producto(tendero_id, deuda_id):
    data = request.get_json()
    if not data:
        return jsonify({'exito': False, 'mensaje': 'No se recibieron datos.'}), 400
    r = DeudaService.agregar_producto(deuda_id, tendero_id,
        data.get('nombre_producto',''), data.get('precio'),
        data.get('cantidad',1))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@deudas_bp.route('/<int:deuda_id>/pagar', methods=['PATCH'])
@token_required
def pagar_deuda(tendero_id, deuda_id):
    r = DeudaService.pagar(deuda_id, tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@deudas_bp.route('/<int:deuda_id>', methods=['DELETE'])
@token_required
def eliminar_deuda(tendero_id, deuda_id):
    r = DeudaService.eliminar(deuda_id, tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']
