# routes/auth.py - Capa de presentación: autenticación
from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.auth_service      import AuthService
from middleware.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    if not data:
        return jsonify({'exito': False, 'mensaje': 'No se recibieron datos.'}), 400
    r = AuthService.registrar(data.get('nombre',''), data.get('email',''),
        data.get('contrasena',''), data.get('nombre_tienda',''), data.get('telefono',''))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'exito': False, 'mensaje': 'No se recibieron datos.'}), 400
    r = AuthService.login(data.get('email',''), data.get('contrasena',''))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@auth_bp.route('/perfil', methods=['GET'])
@token_required
def perfil(tendero_id):
    r = AuthService.obtener_perfil(tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']
