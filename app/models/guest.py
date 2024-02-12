from app import db
from datetime import datetime

class Guest(db.Model):
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    email = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(32), nullable=False)