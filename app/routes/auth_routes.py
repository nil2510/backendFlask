from flask_cors import cross_origin
from flask import Blueprint, jsonify, request
from app.services.auth_service import googleEmail

bp = Blueprint('auth_routes', __name__)

@bp.route('/login-google', methods=['GET'])
@cross_origin()
def loginWithGoogle():
    data = request.get_json()
    if 'email' not in data:
        return jsonify({'error': 'incomplete data'}), 200
    email = data['email']
    
    api_key = googleEmail(email)
    if api_key == None:
        return jsonify({'error': 'invalid credentials'}), 200
    return jsonify({'api_key': api_key}), 200
 