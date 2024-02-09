from flask import Blueprint, request, jsonify
from app.services.request_service import createRequest, getRequests, getRequestsByManager, approveRequestByManager
from app.services.user_service import getUserWithEmpID

bp = Blueprint('request_routes', __name__)


@bp.route('/request', methods=['POST'])
def handlerCreateRequest():
    api_key = request.headers.get('Authorization')
    data = request.get_json()

    if 'date_from' not in data or 'date_to' not in data or 'request_type' not in data:
        return jsonify({'error': 'incomplete data'}), 400

    date_from = data['date_from']
    date_to = data['date_to']
    request_type = data['request_type']

    success = createRequest(api_key, date_from, date_to, request_type)
    if success:
        return jsonify({'message': 'Request sent successfully'}), 201
    else:
        return jsonify({'error': 'Unable to sent request'}), 400

@bp.route('/myrequests', methods=['GET'])
def handlerGetMyRequests():
    api_key = request.headers.get('Authorization')

    requests = getRequests(api_key)

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
        return jsonify({'error': 'No requests found for the given manager'}), 404

@bp.route('/requests', methods=['GET'])
def handlerGetRequests():
    api_key = request.headers.get('Authorization')

    requests = getRequestsByManager(api_key)

    if requests:
        request_details_list = []
        for req in requests:
            user = getUserWithEmpID(req.user_emp_id)
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
        return jsonify({'error': 'No requests found for the given manager'}), 404

@bp.route('/approve-request', methods=['POST'])
def handlerApproveUserByManager():
    api_key = request.headers.get('Authorization')
    data = request.get_json()
    request_id = data.get('request_id')

    if request_id is None:
        return jsonify({'error': 'request_id is required'}), 400
    if api_key is None:
        return jsonify({'error': 'You are not autherised'}), 400

    success = approveRequestByManager(api_key, request_id)

    if success:
        return jsonify({'message': 'Request approved successfully'}), 200
    else:
        return jsonify({'error': 'Request not found or already approved'}), 404