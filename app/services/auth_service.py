from app.models.user import User

def authorize(api_key):
    user = User.query.filter_by(api_key=api_key, status=0).first()
    if user:
        return user.emp_id
    else:
        return None
    
def authorizeAdmin(api_key):
    user = User.query.filter_by(api_key=api_key).first()
    if user:
        return user.user_type
    else:
        return None
    
def googleEmail(email):
    user = User.query.filter_by(email=email, status=0).first()
    if user:
        return user.api_key
    else:
        return None
    