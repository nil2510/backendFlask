from app import db
from datetime import datetime

class User(db.Model):
    emp_id = db.Column(db.String(16), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(32), nullable=False)
    manager_emp_id = db.Column(db.String(16), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=True)