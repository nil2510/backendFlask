from datetime import datetime, timedelta
from app.models.absent import Absent
from app.models.present import Present
from app.models.request import Request
from app.models.user import User
from app import db

def createRequest(api_key, date_from, date_to, request_type):
    user = User.query.filter_by(api_key=api_key, status=0).first()
    status = 1
    if user.user_type == "admin":
        status = 0
    if user:
        request = Request(
            user_emp_id = user.emp_id,
            request_time = datetime.utcnow(),
            approved_time = datetime.utcnow(),
            date_from = date_from,
            date_to = date_to,
            request_type = request_type,
            status = status
            )
        
        db.session.add(request)
        db.session.commit()
        return True
    else:
        return False

def getRequest(emp_id, id):
    requests = Request.query.filter_by(id =id, user_emp_id=emp_id).first()
    return requests

def getRequests(emp_id):
    requests = Request.query.filter_by(user_emp_id=emp_id).all()
    return requests
    
def getRequestByAdmin(id):
    requests = Request.query.filter_by(id= id, status=1).first()
    return requests

def getRequestsByAdmin():
    requests = Request.query.filter_by(status=1).all()
    return requests

def editRequest(user_emp_id, id, new_date_from, new_date_to, new_request_type):
    request = Request.query.filter_by(id=id, user_emp_id=user_emp_id).first()
    if request:
        request.date_from = new_date_from
        request.date_to = new_date_to
        request.request_type = new_request_type
        db.session.commit()
        return True
    else:
        return False

def approveRequestByAdmin(request_id):
        request = Request.query.filter_by(id=request_id, status=1).first()
        if request:
            request.status = 0
            request.approved_time = datetime.utcnow()
            db.session.commit()

            if request.request_type == "absence":
                for date in date_range(request.date_from, request.date_to):
                    absence = Absent(
                        user_emp_id=request.user_emp_id,
                        date=date,
                        reason=request.request_type
                    )
                    db.session.add(absence)

            if request.request_type == "presence":
                for date in date_range(request.date_from, request.date_to):
                    presence = Present(
                        user_emp_id=request.user_emp_id,
                        date=date,
                        check_in=datetime.utcnow(),
                        check_out=datetime.utcnow(),
                    )
                    db.session.add(presence)

            db.session.commit()
            return True

def date_range(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)