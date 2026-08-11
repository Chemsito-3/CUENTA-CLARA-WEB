# routes/dashboard.py - Capa de presentación: dashboard
from flask import Blueprint, request, jsonify
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.dashboard_service import DashboardService
from middleware.auth_middleware  import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/resumen', methods=['GET'])
@token_required
def resumen(tendero_id):
    r = DashboardService.obtener_resumen(tendero_id)
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@dashboard_bp.route('/alertas', methods=['GET'])
@token_required
def alertas(tendero_id):
    r = DashboardService.obtener_alertas(tendero_id, request.args.get('dias',7))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']

@dashboard_bp.route('/top-deudores', methods=['GET'])
@token_required
def top_deudores(tendero_id):
    r = DashboardService.obtener_top_deudores(tendero_id, request.args.get('limite',5))
    return jsonify({k:v for k,v in r.items() if k!='codigo'}), r['codigo']
