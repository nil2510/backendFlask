from datetime import datetime, timedelta
from app.models.absent import Absent
from app.models.present import Present
from app.models.request import Request
from app.models.user import User
from app import db

def createRequest(api_key, date_from, date_to, request_type):
    user = User.query.filter_by(api_key=api_key, status=0).first()
    
    status = 1
    if user.emp_id == user.manager_emp_id:
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

def getRequests(api_key):
    user_emp_id = User.query.filter_by(api_key=api_key).with_entities(User.emp_id).first()
    if user_emp_id:
        user_emp_id = user_emp_id[0]
        requests = Request.query.filter_by(user_emp_id=user_emp_id).all()
        return requests
    return []
    
def getRequestsByManager(api_key):
    manager_emp_id = User.query.filter_by(api_key=api_key).with_entities(User.emp_id).first()
    if manager_emp_id:
        manager_emp_id = manager_emp_id[0]
        user_emp_ids = User.query.filter_by(manager_emp_id=manager_emp_id, status=0).with_entities(User.emp_id).all()
        if user_emp_ids:
            user_emp_ids = [emp_id[0] for emp_id in user_emp_ids]
            requests = Request.query.filter(Request.user_emp_id.in_(user_emp_ids), Request.status == 1).all()
            return requests
    return []


def approveRequestByManager(api_key, request_id):
    manager_emp_id = User.query.filter_by(api_key=api_key).with_entities(User.emp_id).first()

    if manager_emp_id:
        manager_emp_id = manager_emp_id[0]

        request = Request.query.filter_by(id=request_id, status=1).first()
        user = User.query.filter_by(manager_emp_id=manager_emp_id, emp_id=request.user_emp_id).first()

        if request and user:
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

    return False

def date_range(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)