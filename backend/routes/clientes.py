# routes/clientes.py - Capa de presentación: clientes
from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.cliente_service  import ClienteService
from middleware.auth_middleware import token_required

clientes_bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')

@clientes_bp.route('/', methods=['GET'])
@token_required
def get_clientes(tendero_id):
    buscar = request.args.get('buscar','').strip() or None
    r = ClienteService.listar(tendero_id, buscar)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@token_required
def get_cliente(tendero_id, cliente_id):
    r = ClienteService.obtener(cliente_id, tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@clientes_bp.route('/', methods=['POST'])
@token_required
def crear_cliente(tendero_id):
    data = request.get_json()
    if not data:
        return jsonify({'exito': False, 'mensaje': 'No se recibieron datos.'}), 400
    r = ClienteService.crear(tendero_id, data.get('nombre',''),
        data.get('telefono',''), data.get('direccion',''))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@token_required
def actualizar_cliente(tendero_id, cliente_id):
    data = request.get_json()
    if not data:
        return jsonify({'exito': False, 'mensaje': 'No se recibieron datos.'}), 400
    r = ClienteService.actualizar(cliente_id, tendero_id, data)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@token_required
def eliminar_cliente(tendero_id, cliente_id):
    r = ClienteService.eliminar(cliente_id, tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']
