from app.models.user import User
from app import db

def checkEmail(email):
    user = User.query.filter_by(email=email, status=0).first()
    if user:
        return user.api_key
    else:
        return None