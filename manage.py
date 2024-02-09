from flask.cli import FlaskGroup
from flask_cors import CORS, cross_origin
from app import create_app, db
from dotenv import load_dotenv
import os

load_dotenv()
google_client_secret = os.getenv('google_client_secret')

app = create_app
cli = FlaskGroup(app)
# CORS(app, resources={r"*": {"origins": "http://localhost:4200"}})

@cli.command('create_db')
def create_db():
    db.create_all()

if __name__ == '__main__':
    app.secret_key = google_client_secret
    # db.create_all()
    cli()