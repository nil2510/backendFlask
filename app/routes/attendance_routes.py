from flask import Blueprint, jsonify

from app.services.attendance_service import getAttendance, getMyAttendance

bp = Blueprint('attendance_routes', __name__)

@bp.route('/my-attendance', methods=['GET'])
def handlerMyAttendance():
    # getMyAttendance(api_key)
    return
@bp.route('/attendance', methods=['GET'])
def handlerAttendance():
    # getAttendance(api_key, emp_id)
    return