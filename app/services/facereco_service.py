import datetime
from app.models.present import Present
from app import db

def check_in(user_id):
    new_attendance = Present(user_id=user_id)
    db.session.add(new_attendance)
    db.session.commit()
    return new_attendance

def check_out(attendance_id):
    attendance = Present.query.get(attendance_id)
    if attendance:
        attendance.check_out = datetime.utcnow()
        db.session.commit()
        return attendance
    return None
