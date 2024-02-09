from app import db
from datetime import datetime

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_emp_id = db.Column(db.String(16), db.ForeignKey('user.emp_id'), nullable=False)
    request_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    approved_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    request_type = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Integer, nullable=False, default = 1)
