from flask import Blueprint, jsonify, request
from app.services.auth_service import authorizeAdmin
from app.services.guest_services import createGuest, deleteGuest, editGuest, getGuest, getGuests

bp = Blueprint('guest_routes', __name__)

@bp.route('/create-guest', methods=['POST'])
def handlerCreateGuest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400

    data = request.get_json()
    if 'from' not in data or 'to' not in data or 'name' not in data or 'email' not in data or 'company' not in data:
        return jsonify({'error': 'incomplete data'}), 400
    
    planned_from = data['from']
    planned_to = data['to']
    name = data['name']
    email = data['email']
    company = data['company']

    success = createGuest(planned_from, planned_to, name, email, company)
    if success:
        return jsonify({'message': 'Guest registered successfully'}), 201
    else :
        return jsonify({'error': 'Unable to create guest'}), 201
    


@bp.route('/guest', methods=['GET'])
def handlerGuest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400
    
    data = request.get_json()
    if 'id' not in data:
        return jsonify({'error': 'incomplete data'}), 400
    
    id = data['id']
    guest = getGuest(id)

    if guest:
        guest_details = {
            'planned_from': guest.planned_from,
            'planned_to': guest.planned_to,
            'name': guest.name,
            'email': guest.email,
            'company': guest.position
        }
        return jsonify(guest_details)
    else:
        return jsonify({'error': 'User not found'}), 404
    

@bp.route('/guests', methods=['GET'])
def handlerGuests():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400
    
    guests = getGuests()

    if guests:
        guest_details_list = []
        for guest in guests:
            guest_details = {
                'planned_from': guest.planned_from,
                'planned_to': guest.planned_to,
                'name': guest.name,
                'email': guest.email,
                'company': guest.position
            }
            guest_details_list.append(guest_details)

        return jsonify(guest_details_list)
    else:
        return jsonify({'error': 'No guests found'}), 404


@bp.route('/edit-guest', methods=['PUT'])
def handlerEditGuest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400

    data = request.get_json()
    id = data.get('id')
    planned_from = data.get('planned_from')
    planned_to = data.get('planned_to')
    name = data.get('name')
    email = data.get('email')
    company = data.get('company')

    success = editGuest(id, planned_from, planned_to, name, email, company)
    if success:
        return jsonify({'message': 'Guest edited successfully'}), 200
    else:
        return jsonify({'error': 'Guest not found or error occurred during editing'}), 404


@bp.route('/delete-guest', methods=['DELETE'])
def handlerDeleteGuest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400
    
    data = request.get_json()
    id = data.get('id')

    success = deleteGuest(id)
    if success:
        return jsonify({'message': 'Guest deleted successfully'}), 200
    else:
        return jsonify({'error': 'Guest not found or error occurred during deletion'}), 404
