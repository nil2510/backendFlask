from datetime import datetime
from app import db
from app.models.guest import Guest

def createGuest(planned_from, planned_to, name, email, company):
    guest = Guest(
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
        planned_from = planned_from,
        planned_to = planned_to,
        name = name,
        email = email,
        company = company,
        check_in = datetime.utcnow(),
        check_out = datetime.utcnow()
        )
    db.session.add(guest)
    db.session.commit()
    return True

def getGuest(id):
    guest = Guest.query.filter_by(id=id).first()
    return guest

def getGuests():
    guests = Guest.query.all()
    return guests

def editGuest(id, new_planned_from, new_planned_to, new_name, new_email, new_company):
    guest = Guest.query.filter_by(id=id).first()
    if guest:
        guest.planned_from = new_planned_from
        guest.planned_to = new_planned_to
        guest.name = new_name
        guest.email = new_email
        guest.company = new_company
        guest.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    else:
        return False
    
def deleteGuest(id):
    guest = Guest.query.filter_by(id=id).first()
    if guest:
        db.session.delete(guest)
        db.session.commit()
        return True
    else:
        return False