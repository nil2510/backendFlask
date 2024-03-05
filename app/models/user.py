from app import db
from datetime import datetime

class User(db.Model):
    emp_id = db.Column(db.String(16), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(32), nullable=False)
    mobile = db.Column(db.String(16), nullable=False, unique=True)
    manager_name = db.Column(db.String(16), nullable=False)
    user_type = db.Column(db.String(16), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    api_key = db.Column(db.String(64), nullable=False, unique=True)
    
# class Employee(db.Model):
#     # emp_id = db.Column(db.String(16), primary_key=True)
#     id = db.Column(db.String(32), primary_key = True)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
#     updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
#     email = db.Column(db.String(64), nullable=False, unique=True)
#     # password = db.Column(db.String(32), nullable=False)
#     name = db.Column(db.String(64), nullable=False)
#     # position = db.Column(db.String(32), nullable=False)
#     # mobile = db.Column(db.String(16), nullable=False, unique=True)
#     manager_id = db.Column(db.String(16), nullable=False)
#     gender = db.Column(db.String(16), nullable = False)
#     # user_type = db.Column(db.String(16), nullable=False)
#     status = db.Column(db.Integer, nullable=False)
    # api_key = db.Column(db.String(64), nullable=False, unique=True)