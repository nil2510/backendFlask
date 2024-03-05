import base64
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.auth_service import authorize, authorizeAdmin
from app.services.facereco_service import deleteFace, trainFace
from app.services.user_service import approveUserByAdmin, changePassword, createUser, deleteUserByAdmin, editUserByAdmin, getUnapprrovedUsersByAdmin, getUser, getUsersByAdmin, checkUser

bp = Blueprint('user_routes', __name__)

load_dotenv()
IMAGE_SERVER_PATH = os.getenv('IMAGE_SERVER_PATH') + "/users"
os.makedirs(IMAGE_SERVER_PATH, exist_ok=True)

def is_valid_base64(data):
    return bool(data.startswith('data:image/') and ';base64,' in data)

@bp.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    required_fields = ['emp_id', 'name', 'email', 'position', 'mobile', 'password', 'manager_name', 'user_type', 'image_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"Missing required field: {field}"}), 400
    
    emp_id = data['emp_id']
    email = data['email']
    password = data['password']
    name = data['name']
    position = data['position']
    mobile = data['mobile']
    manager_name = data['manager_name']
    user_type = data['user_type']

    EMP_IMAGE_SERVER_PATH = IMAGE_SERVER_PATH + "/" + emp_id
    os.makedirs(EMP_IMAGE_SERVER_PATH, exist_ok=True)
    IMAGE_NAME = emp_id + ".jpg"

    base64_string = data['image_data']
    with open(os.path.join(EMP_IMAGE_SERVER_PATH, IMAGE_NAME), 'wb') as f:
        f.write(base64.b64decode(base64_string.split(',')[1]))

    user, error = createUser(emp_id, name, email, position, mobile, password, manager_name, user_type)
    if user:
        return jsonify({'message': 'User registered successfully', 'api_key': user.api_key, "user_type":user.user_type}), 201
    if error:
        return jsonify({'error': f'{error}'}), 201

@bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'incomplete data'}), 200
    email = data['email']
    password = data['password']
    
    user = checkUser(email, password)
    if user:
        return jsonify({'api_key': user.api_key, "user_type": user.user_type}), 200
    else:
        return jsonify({'error': 'invalid credentials'}), 200

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
        return jsonify({'error': 'No users found'}), 404
    

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
        return jsonify({'error': 'No pending users found'}), 404

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
    trainFace("E0009744")
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