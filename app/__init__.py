from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import auth_routes
    from app.routes import user_routes
    from app.routes import request_routes
    from app.routes import attendance_routes
    from app.routes import facereco_routes

    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(request_routes.bp)
    app.register_blueprint(attendance_routes.bp)
    app.register_blueprint(facereco_routes.bp)
    return app
