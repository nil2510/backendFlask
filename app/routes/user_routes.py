from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.user_service import approveUserByManager, changePassword, create_user, deleteUserByManager, editUserByManager, getEmpID, getUnapprrovedUsersByManager, getUser, getUsersByManager

bp = Blueprint('user_routes', __name__)

@bp.route('/register-user', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()

    if 'emp_id' not in data or 'name' not in data or 'email' not in data or 'position' not in data or 'password' not in data or 'manager_emp_id' not in data:
        return jsonify({'error': 'incomplete data'}), 400
    
    emp_id = data['emp_id']
    email = data['email']
    password = data['password']
    name = data['name']
    position = data['position']
    manager_emp_id = data['manager_emp_id']

    user = create_user(emp_id, name, email, position, password, manager_emp_id)

    return jsonify({'message': 'User registered successfully', 'api_key': user.api_key}), 201

@bp.route('/login-user', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'incomplete data'}), 200
    
    email = data['email']
    password = data['password']
    
    api_key = getEmpID(email, password)
    if api_key == None:
        return jsonify({'error': 'invalid credentials'}), 200
    return jsonify({'api_key': api_key}), 200

@bp.route('/user', methods=['GET'])
@cross_origin()
def handlerGetUser():
    api_key = request.headers.get('Authorization')

    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400

    user = getUser(api_key)

    if user:
        user_details = {
            'emp_id': user.emp_id,
            'name': user.name,
            'email': user.email,
            'position': user.position,
            'manager_emp_id': user.manager_emp_id
        }
        return jsonify(user_details)
    else:
        return jsonify({'error': 'User not found'}), 404
    
@bp.route('/users', methods=['GET'])
def handlerGetUsersByManager():
    api_key = request.headers.get('Authorization')

    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400

    users = getUsersByManager(api_key)

    if users:
        user_details_list = []
        for user in users:
            user_details = {
                'emp_id': user.emp_id,
                'name': user.name,
                'email': user.email,
                'position': user.position
            }
            user_details_list.append(user_details)

        return jsonify(user_details_list)
    else:
        return jsonify({'error': 'No users found for the given manager'}), 404
    

@bp.route('/pending-users', methods=['GET'])
def handlerGetPendingUsersByManager():
    api_key = request.headers.get('Authorization')

    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400

    pending_users = getUnapprrovedUsersByManager(api_key)

    if pending_users:
        pending_users_list = []
        for user in pending_users:
            user_details = {
                'emp_id': user.emp_id,
                'name': user.name,
                'email': user.email,
                'position': user.position
            }
            pending_users_list.append(user_details)

        return jsonify(pending_users_list)
    else:
        return jsonify({'error': 'No pending users found for the given manager'}), 404

@bp.route('/approve-user', methods=['POST'])
def handlerApproveUserByManager():
    api_key = request.headers.get('Authorization')
    data = request.get_json()
    emp_id = data.get('emp_id')

    if emp_id is None:
        return jsonify({'error': 'emp_id is required'}), 400
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400

    success = approveUserByManager(api_key, emp_id)

    if success:
        return jsonify({'message': 'User approved successfully'}), 200
    else:
        return jsonify({'error': 'User not found or already approved'}), 404

@bp.route('/edit-user', methods=['PUT'])
def handlerEditUserByManager():
    api_key = request.headers.get('Authorization')
    data = request.get_json()

    emp_id = data.get('emp_id')
    new_name = data.get('new_name')
    new_email = data.get('new_email')
    new_position = data.get('new_position')
    new_manager_emp_id = data.get('new_manager_emp_id')

    if emp_id is None:
        return jsonify({'error': 'emp_id is required'}), 400

    success = editUserByManager(api_key, emp_id, new_name, new_email, new_position, new_manager_emp_id)

    if success:
        return jsonify({'message': 'User edited successfully'}), 200
    else:
        return jsonify({'error': 'User not found or error occurred during editing'}), 404


@bp.route('/delete-user', methods=['DELETE'])
def handlerDeleteUserByManager():
    api_key = request.headers.get('Authorization')
    data = request.get_json()

    emp_id = data.get('emp_id')

    if emp_id is None:
        return jsonify({'error': 'emp_id is required'}), 400

    success = deleteUserByManager(api_key, emp_id)

    if success:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found or error occurred during deletion'}), 404
    

@bp.route('/edit-password', methods=['PUT'])
def handlerEditPassword():
    api_key = request.headers.get('Authorization')
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if api_key is None:
        return jsonify({'error': 'Not Autherised'}), 400

    success = changePassword(api_key, old_password, new_password)

    if success:
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'error': 'Can not change Password'}), 404