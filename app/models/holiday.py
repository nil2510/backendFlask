from app import db

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(64), nullable=False)