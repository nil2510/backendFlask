from datetime import datetime
from app.models.user import User
from app import db

import hashlib
import secrets

def generate_api_key():
    """Generates a random API key using SHA-256 hashing."""
    random_bytes = secrets.token_bytes(32)  # Generate 32 random bytes
    api_key = hashlib.sha256(random_bytes).hexdigest()  # Hash using SHA-256
    return api_key

def validateEmail(email):
    user = User.query.filter(email == email).first()
    if user:
        return False
    return True
        
def validateMobile(mobile):
    user = User.query.filter(mobile == mobile).first()
    if user:
        return False
    return True

def create_user(emp_id, name, email, position, mobile, password, manager_emp_id):
    status = 1
    if emp_id == manager_emp_id:
        status = 0

    user = User(
        emp_id = emp_id,
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
        email = email,
        password = password,
        name = name,
        position = position,
        mobile = mobile,
        manager_emp_id = manager_emp_id,
        status = status,
        api_key = generate_api_key()
        )
    
    db.session.add(user)
    db.session.commit()

    return user.api_key


def getEmpID(email, password):
    user = User.query.filter_by(email=email, password=password, status=0).first()
    if user:
        return user.api_key
    else:
        return None

def getUser(api_key):
    user = User.query.filter_by(api_key=api_key).first()
    return user
def getUserWithEmpID(emp_id):
    user = User.query.filter_by(emp_id=emp_id).first()
    return user

def getUsersByManager(api_key):
    subquery = User.query.filter_by(api_key=api_key).with_entities(User.emp_id).subquery()
    users = User.query.filter(User.manager_emp_id.in_(subquery)).filter_by(status=0).all()
    return users

def getUnapprrovedUsersByManager(api_key):
    subquery = User.query.filter_by(api_key=api_key).with_entities(User.emp_id).subquery()
    users = User.query.filter(User.manager_emp_id.in_(subquery)).filter_by(status=1).all()
    return users

def approveUserByManager(api_key, emp_id):
    manager = User.query.filter_by(api_key=api_key).first()
    user = User.query.filter_by(emp_id=emp_id, status=1).first()

    if user.manager_emp_id != manager.emp_id:
        return False

    if user:
        user.status = 0
        db.session.commit()
        return True
    else:
        return False

def editUserByManager(api_key, emp_id, new_name, new_email, new_position, new_mobile, new_manager_emp_id):
    manager = User.query.filter_by(api_key=api_key).first()
    user = User.query.filter_by(emp_id=emp_id).first()

    if user.manager_emp_id != manager.emp_id:
        return False

    if user:
        user.name = new_name
        user.email = new_email
        user.position = new_position
        user.mobile = new_mobile
        user.updated_at = datetime.utcnow()
        user.manager_emp_id = new_manager_emp_id

        db.session.commit()
        return True
    else:
        return False
    
def deleteUserByManager(api_key, emp_id):
    manager = User.query.filter_by(api_key=api_key).first()
    user = User.query.filter_by(emp_id=emp_id).first()

    if user.manager_emp_id != manager.emp_id:
        return False

    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    else:
        return False
    
def changePassword(api_key, old_password, new_password):
    user = User.query.filter_by(api_key=api_key).first()

    if old_password != user.password:
        return False
    if new_password == old_password:
        return False
    if user:
        user.password = new_password
        user.updated_at = datetime.utcnow()

        db.session.commit()
        return True
    else:
        return False