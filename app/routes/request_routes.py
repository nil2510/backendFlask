from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.auth_service import authorize, authorizeAdmin
from app.services.request_service import approveRequestByAdmin, createRequest, editRequest, getRequest, getRequestByAdmin, getRequests, getRequestsByAdmin
from app.services.user_service import getUser

bp = Blueprint('request_routes', __name__)

@bp.route('/request', methods=['POST'])
@cross_origin()
def handlerCreateRequest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400

    data = request.get_json()
    if 'date_from' not in data or 'date_to' not in data or 'request_type' not in data:
        return jsonify({'error': 'incomplete data'}), 400
    date_from = data['date_from']
    date_to = data['date_to']
    request_type = data['request_type']

    success = createRequest(emp_id, date_from, date_to, request_type)
    if success:
        return jsonify({'message': 'Request sent successfully'}), 201
    else:
        return jsonify({'error': 'Unable to sent request'}), 400
    
@bp.route('/myrequest', methods=['GET'])
@cross_origin()
def handlerGetMyRequest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400
    
    req = getRequest(emp_id, id)
    if req:
        req_details = {
            'request_id': req.id,
            'request_time': req.request_time,
            'date_from': req.date_from,
            'date_to': req.date_to,
            'request_type': req.request_type,
            'status': req.status
        }
        return jsonify(req_details)
    else:
        return jsonify({'error': 'Request not found'}), 404

@bp.route('/myrequests', methods=['GET'])
@cross_origin()
def handlerGetMyRequests():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400

    requests = getRequests(emp_id)
    if requests:
        request_details_list = []
        for req in requests:
            request_details = {
                'request_id': req.id,
                'request_time': req.request_time,
                'date_from': req.date_from,
                'date_to': req.date_to,
                'request_type': req.request_type,
                'status': req.status
            }
            request_details_list.append(request_details)

        return jsonify(request_details_list)
    else:
        return jsonify({'error': 'No requests found'}), 404
    

@bp.route('/request', methods=['GET'])
@cross_origin()
def handlerGetRequest():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400
    
    req = getRequestByAdmin(id)
    if req:
        user = getUser(req.user_emp_id)
        req_details = {
            'request_id': req.id,
            'user_name': user.name,
            'user_emp_id': req.user_emp_id,
            'request_time': req.request_time,
            'date_from': req.date_from,
            'date_to': req.date_to,
            'request_type': req.request_type
        }
        return jsonify(req_details)
    else:
        return jsonify({'error': 'Request not found'}), 404



@bp.route('/requests', methods=['GET'])
@cross_origin()
def handlerGetRequests():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400

    requests = getRequestsByAdmin()
    if requests:
        request_details_list = []
        for req in requests:
            user = getUser(req.user_emp_id)
            request_details = {
                'request_id': req.id,
                'user_name': user.name,
                'user_emp_id': req.user_emp_id,
                'request_time': req.request_time,
                'date_from': req.date_from,
                'date_to': req.date_to,
                'request_type': req.request_type
            }
            request_details_list.append(request_details)
        return jsonify(request_details_list)
    else:
        return jsonify({'error': 'No requests found'}), 404
    

@bp.route('/edit-request', methods=['PUT'])
@cross_origin()
def handlerEditUserByManager():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    emp_id = authorize(api_key)
    if emp_id is None:
        return jsonify({'error': 'you are not registered'}), 400

    data = request.get_json()
    if 'id' not in data or 'new_date_from' not in data or 'new_date_to' not in data or 'new_request_type' not in data:
        return jsonify({'error': 'incomplete data'}), 200  
    user_emp_id = emp_id
    id = data.get('id')
    new_date_from = data.get('new_date_from')
    new_date_to = data.get('new_date_to')
    new_request_type = data.get('new_request_type')

    success = editRequest(user_emp_id, id, new_date_from, new_date_to, new_request_type)
    if success:
        return jsonify({'message': 'Request edited successfully'}), 200
    else:
        return jsonify({'error': 'Request not found or error occurred during editing'}), 404
    

@bp.route('/approve-request', methods=['POST'])
@cross_origin()
def handlerApproveUserByManager():
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return jsonify({'error': 'you are not autherised'}), 400
    user_type = authorizeAdmin(api_key)
    if user_type != "admin":
        return jsonify({'error': 'you are not autherised'}), 400
    
    data = request.get_json()
    if 'request_id' not in data :
        return jsonify({'error': 'incomplete data'}), 400
    request_id = data.get('request_id')

    success = approveRequestByAdmin(request_id)
    if success:
        return jsonify({'message': 'Request approved successfully'}), 200
    else:
        return jsonify({'error': 'Request not found or already approved'}), 404