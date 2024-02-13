from flask import Blueprint, request, jsonify
from app.services.auth_service import authorize, authorizeAdmin
from app.services.attendance_service import getAttendance

bp = Blueprint('attendance_routes', __name__)

@bp.route('/my-attendance', methods=['GET'])
def handlerMyAttendance():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400
    
    getAttendance(emp_id)
    
    return
@bp.route('/attendance', methods=['GET'])
def handlerAttendance():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400
    
    data = request.get_json()
    if 'emp_id' not in data:
        return jsonify({'error': 'incomplete data'}), 200
    emp_id = data.get('emp_id')

    getAttendance(emp_id)
    
    return