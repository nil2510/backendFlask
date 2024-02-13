from datetime import datetime
from flask import Blueprint, jsonify
from app.models.guest import Guest
from app.models.present import Present
from app.models.user import User
from app.services.facereco_service import check_in, check_out, face_match
from app import db

bp = Blueprint('presence_routes', __name__)

@bp.route('/recognise', methods=['POST'])
def check_in():
    employee_id =  face_match('C:/Users/SunilPradhan/Desktop/Airport AMS/images/captured_image/captured_image.jpg','C:/Users/SunilPradhan/Desktop/Airport AMS/backendFlask/data.pt')
    if employee_id == 'Unknown':
      return jsonify({'message':'Employee not found', 'emp_id': 'unknown'})
    
    user = User.query.filter_by(emp_id = employee_id).first()
    if user:
        today_record = Present.query.filter_by(user_emp_id=employee_id, date=datetime.now().date()).first()
        if today_record:
            today_record.check_out = datetime.utcnow().time()
            db.session.commit()
            return jsonify({'message':'Your exit time has been updated','name': user.name})
        else:
            present = Present(
                user_emp_id = user.emp_id,
                date = datetime.utcnow().date(),
                check_in = datetime.utcnow().time(),
                check_out = datetime.utcnow().time()
            )
            db.session.add(present)
            db.session.commit()
            return jsonify({'message':'Your attendance has been marked', 'name': user.name})


    guest = Guest.query.filter_by(id = employee_id).first()
    if guest:
        if guest.updated_at == guest.check_in:
            guest.check_in = datetime.utcnow()
            db.session.commit()
            return jsonify({'message':'Your entry time has been marked', 'name': guest.name})
        else:
            guest.check_out = datetime.utcnow()
            db.session.commit()
            return jsonify({'message':'Your exit time has been updated','name': guest.name})
            
