import base64
from datetime import datetime
from dotenv import load_dotenv
import os
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from app.models.guest import Guest
from app.models.present import Present
from app.models.user import User
from app.services.facereco_service import recogniseFace
from app import db

bp = Blueprint('facereco_routes', __name__)

load_dotenv()
IMAGE_SERVER_PATH = os.getenv('IMAGE_SERVER_PATH') + "/captured_image"
os.makedirs(IMAGE_SERVER_PATH, exist_ok=True)

def is_valid_base64(data):
    return bool(data.startswith('data:image/') and ';base64,' in data)

@bp.route('/recognise', methods=['POST'])
@cross_origin()
def recognise():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'message': 'Missing image data','name': "unknown"}), 400
    if not is_valid_base64(data['image']):
        return jsonify({'message': 'Invalid image format','name': "unknown"}), 400

    base64_string = data['image']
    with open(os.path.join(IMAGE_SERVER_PATH, "captured_image.jpg"), 'wb') as f:
        f.write(base64.b64decode(base64_string.split(',')[1]))

    employee_id = recogniseFace()
    if employee_id == 'Unknown':
        return jsonify({'message':'Employee not found!','name': "unknown"})
    
    user = User.query.filter_by(emp_id = employee_id).first()
    if user:
        today_record = Present.query.filter_by(user_emp_id=employee_id, date=datetime.now().date()).first()
        if today_record:
            today_record.check_out = datetime.utcnow().time()
            db.session.commit()
            return jsonify({'message':'Your exit time has been updated.','name': user.name})
        else:
            present = Present(
                user_emp_id = user.emp_id,
                date = datetime.utcnow().date(),
                check_in = datetime.utcnow().time(),
                check_out = datetime.utcnow().time()
            )
            db.session.add(present)
            db.session.commit()
            return jsonify({'message':'Your attendance has been marked.', 'name': user.name})

    guest = Guest.query.filter_by(id = employee_id).first()
    if guest:
        if guest.updated_at == guest.check_in:
            guest.check_in = datetime.utcnow()
            db.session.commit()
            return jsonify({'message':'Your entry time has been marked.', 'name': guest.name})
        else:
            guest.check_out = datetime.utcnow()
            db.session.commit()
            return jsonify({'message':'Your exit time has been updated.','name': guest.name})
    
    return jsonify({'message':'Employee not found','name': "unknown"})