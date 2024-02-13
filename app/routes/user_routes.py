from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.auth_service import authorize, authorizeAdmin
from app.services.facereco_service import deleteFace, trainFace
from app.services.user_service import approveUserByAdmin, changePassword, createUser, deleteUserByAdmin, editUserByAdmin, getUnapprrovedUsersByAdmin, getUser, getUsersByAdmin, validateEmail, validateMobile, validateUser

bp = Blueprint('user_routes', __name__)

@bp.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    if 'emp_id' not in data or 'name' not in data or 'email' not in data or 'position' not in data or 'mobile' not in data or 'password' not in data or 'manager_name' not in data or 'user_type' not in data:
        return jsonify({'error': 'incomplete data'}), 400
    emp_id = data['emp_id']
    email = data['email']
    password = data['password']
    name = data['name']
    position = data['position']
    mobile = data['mobile']
    manager_name = data['manager_name']
    user_type = data['user_type']

    success = validateEmail(email)
    if success:
        return jsonify({'error': 'email is already registered'}), 200
    
    success = validateMobile(mobile)
    if success:
        return jsonify({'error': 'mobile is already registered'}), 200

    user = createUser(emp_id, name, email, position, mobile, password, manager_name, user_type)

    return jsonify({'message': 'User registered successfully', 'api_key': user.api_key, "user_type":user.user_type}), 201

@bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'incomplete data'}), 200
    email = data['email']
    password = data['password']
    
    api_key = validateUser(email, password)
    if api_key == None:
        return jsonify({'error': 'invalid credentials'}), 200
    return jsonify({'api_key': api_key}), 200

@bp.route('/user', methods=['GET'])
@cross_origin()
def handlerGetUser():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400

    user = getUser(emp_id)
    if user:
        user_details = {
            'emp_id': user.emp_id,
            'name': user.name,
            'email': user.email,
            'position': user.position,
            'number': user.number,
            'manager_name': user.manager_name
        }
        return jsonify(user_details)
    else:
        return jsonify({'error': 'User not found'}), 404
    
@bp.route('/users', methods=['GET'])
@cross_origin()
def handlerGetUsersByAdmin():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400

    users = getUsersByAdmin()
    if users:
        user_details_list = []
        for user in users:
            user_details = {
                'emp_id': user.emp_id,
                'name': user.name,
                'email': user.email,
                'position': user.position,
                'number': user.number,
                'manager_name': user.manager_name
            }
            user_details_list.append(user_details)

        return jsonify(user_details_list)
    else:
        return jsonify({'error': 'No users found for the given manager'}), 404
    

@bp.route('/pending-users', methods=['GET'])
@cross_origin()
def handlerGetPendingUsersByAdmin():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400

    pending_users = getUnapprrovedUsersByAdmin()
    if pending_users:
        pending_users_list = []
        for user in pending_users:
            user_details = {
                'emp_id': user.emp_id,
                'name': user.name,
                'email': user.email,
                'position': user.position,
                'number': user.number,
                'manager_name': user.manager_name
            }
            pending_users_list.append(user_details)
        return jsonify(pending_users_list)
    else:
        return jsonify({'error': 'No pending users found for the given manager'}), 404

@bp.route('/approve-user', methods=['POST'])
@cross_origin()
def handlerApproveUserByAdmin():
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

    success = approveUserByAdmin(emp_id)
    trainFace()
    if success:
        return jsonify({'message': 'User approved successfully'}), 200
    else:
        return jsonify({'error': 'User not found or already approved'}), 404

@bp.route('/edit-user', methods=['PUT'])
@cross_origin()
def handlerEditUserByAdmin():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400

    data = request.get_json()
    if 'emp_id' not in data or 'new_name' not in data or 'new_email' not in data or 'new_position' not in data or 'new_mobile' not in data or 'new_manager_name' not in data:
        return jsonify({'error': 'incomplete data'}), 200  
    emp_id = data.get('emp_id')
    new_name = data.get('new_name')
    new_email = data.get('new_email')
    new_position = data.get('new_position')
    new_mobile = data.get('new_mobile')
    new_manager_name = data.get('new_manager_name')

    success = editUserByAdmin(emp_id, new_name, new_email, new_position, new_mobile, new_manager_name)
    if success:
        return jsonify({'message': 'User edited successfully'}), 200
    else:
        return jsonify({'error': 'User not found or error occurred during editing'}), 404


@bp.route('/delete-user', methods=['DELETE'])
@cross_origin()
def handlerDeleteUserByAdmin():
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

    success = deleteUserByAdmin(emp_id)
    deleteFace(emp_id)
    if success:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found or error occurred during deletion'}), 404
    

@bp.route('/edit-password', methods=['PUT'])
@cross_origin()
def handlerEditPassword():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400
    
    data = request.get_json()
    if 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'incomplete data'}), 200
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    success = changePassword(emp_id, old_password, new_password)
    if success:
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'error': 'Can not change Password'}), 404