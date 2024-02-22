from datetime import datetime
from flask.cli import FlaskGroup
from app import create_app, db
from app.models.holiday import Holiday

app = create_app
cli = FlaskGroup(app)

@cli.command('create_db')
def create_db():
    db.create_all()
    if not Holiday.query.filter_by(date=datetime(2024, 1, 1)).first():
        sample_data = [
            (datetime(2024, 1, 1), "New Year's Day"),
            (datetime(2024, 1, 15), "Sankranti / Pongal"),
            (datetime(2024, 1, 26), "Republic Day"),
            (datetime(2024, 2, 18), "Mahashivratri"),
            (datetime(2024, 4, 7), "Good Friday"),
            (datetime(2024, 4, 22), "Eid-Ul-Fitr"),
            (datetime(2024, 5, 1), "May Day"),
            (datetime(2024, 6, 29), "Bakra Id"),
            (datetime(2024, 8, 15), "Independence Day"),
            (datetime(2024, 9, 19), "Ganesh Chathurthi"),
            (datetime(2024, 10, 2), "Gandhi Jayanti"),
            (datetime(2024, 10, 24), "Dusshera"),
            (datetime(2024, 11, 12), "Diwali"),
            (datetime(2024, 11, 13), "Balipadyami Diwali / Govardhan Pooja"),
            (datetime(2024, 12, 25), "Christmas"),
        ]
        for date, title in sample_data:
            if not Holiday.query.filter_by(date=date).first():
                db.session.add(Holiday(date=date, title=title))
        db.session.commit()

if __name__ == '__main__':
    cli()
