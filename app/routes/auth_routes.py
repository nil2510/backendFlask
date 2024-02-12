from dotenv import load_dotenv
import os
from flask_cors import cross_origin
from flask import Blueprint, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

from app.services.auth_service import checkEmail

oauth = OAuth()
bp = Blueprint('auth_routes', __name__)

load_dotenv()

google_client_id = os.getenv('google_client_id')
google_client_secret = os.getenv('google_client_secret')
google_redirect_uri = os.getenv('google_redirect_uri')

google = oauth.remote_app(
    'google',
    consumer_key=google_client_id,
    consumer_secret=google_client_secret,
    request_token_params={
        'scope': 'openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read',
    },
    base_url='https://www.googleapis.com/oauth2/v3/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@google.tokengetter
@cross_origin()
def get_google_oauth_token():
    return session.get('google_token')

@bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    return google.authorize(callback=url_for('auth_routes.authorized', _external=True))

@bp.route('/login/authorized')
@cross_origin()
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return jsonify({'error': 'login failed'}), 400

    session['google_token'] = (response['access_token'], '')

    me = google.get('userinfo')
    json_data = {'data': me.data}
    data = json_data['data']

    email = data['email']
    api_key = checkEmail(email)
    if api_key:
        return jsonify({'api_key': api_key}), 200

@bp.route('/logout', methods=['PUT'])
@cross_origin()
def logout():
    session.pop('google_token', None)
    return jsonify({'msg': 'logout successful'}), 400