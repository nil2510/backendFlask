from app import db
from datetime import datetime

class Present(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_emp_id = db.Column(db.String(16), db.ForeignKey('user.emp_id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    check_in = db.Column(db.Time, nullable=False, default=datetime.utcnow().time())
    check_out = db.Column(db.Time, nullable=False, default=datetime.utcnow().time())  
