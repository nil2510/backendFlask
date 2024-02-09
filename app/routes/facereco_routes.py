from flask import Blueprint, jsonify
from app.services.facereco_service import check_in, check_out

bp = Blueprint('presence_routes', __name__)

@bp.route('/check-in', methods=['POST'])
def check_in():
    # Implement check-in logic here
    return jsonify({'message': 'Check-in route'})

@bp.route('/check-out', methods=['POST'])
def check_out():
    # Implement check-out logic here
    return jsonify({'message': 'Check-out route'})
