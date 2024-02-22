from app.models.absent import Absent
from app.models.holiday import Holiday
from app.models.present import Present

def getAttendance(emp_id):
    attendance_list = []

    presents = Present.query.filter_by(user_emp_id=emp_id).all()
    if presents:
        for present in presents:
            present_details = {
                'date': present.date,
                'att_type': "present",
                'reason': "present",
            }
            attendance_list.append(present_details)

    absents = Absent.query.filter_by(user_emp_id=emp_id).all()
    if absents:
        for absent in absents:
            absent_details = {
                'date': absent.date,
                'att_type': 'absent',
                'reason': absent.reason,
            }
            attendance_list.append(absent_details)

    holidays = Holiday.query.all()
    if holidays:
        for holiday in holidays:
            holiday_details = {
                'date': holiday.date,
                'att_type': 'holiday',
                'reason': holiday.title,
            }
            attendance_list.append(holiday_details)


    return attendance_list