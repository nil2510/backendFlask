from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

class Config:
    
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/{}'.format(
        MYSQL_USERNAME, MYSQL_PASSWORD, DB_NAME
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = SECRET_KEY
