
from .detection import face_match, real_time_face_detection, train_unknowns

@app.route('/employees', methods=['POST'])
@cross_origin()
def add_employee():
    data = request.get_json()
    emp_id = data.get('emp_id')
    print("Employee id is -------", emp_id)

    # Check if the employee with the given emp_id exists
    existing_employee = Employee.query.filter_by(emp_id=emp_id).first()

    if existing_employee:
        # Update existing employee record
        existing_employee.emp_name = str(data['emp_name'])
        existing_employee.job_position = str(data['job_position'])
        existing_employee.contact_no = str(data['contact_no'])
        existing_employee.email = str(data['email'])
        existing_employee.username = str(data['username'])
        # existing_employee.set_password(data['password'])
        if 'password' in data and data['password']:
          existing_employee.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        db.session.commit()
        return jsonify({'message': 'Employee updated successfully'})
    else:
        img_path = f'D:/database/frontend/Face-Recognition-frontend/src/assets'
        train_unknowns(img_path, 'D:/database/frontend/Face-Recognition-frontend/data.pt')

        # Create a new employee record
        new_employee = Employee(
            emp_id=data['emp_id'],
            emp_name=data['emp_name'],
            job_position=data['job_position'],
            email=data['email'],
            role=data['role'],
            contact_no=data['contact_no'],
        )

        db.session.add(new_employee)
        db.session.commit()

        return jsonify({'message': 'Employee added successfully'})


@app.route('/attendance/<string:image_path>', methods=['POST'])
def mark_entry_exit(image_path):
    current_time = datetime.utcnow()
    data = request.json
    # image_data = base64.b64decode(image_path)
    print("image_path is -------",image_path)
    # employee_id = face_match('C:/Users/SahithReddy/Desktop/python/src/assets/captured_image.jpg','C:/Users/SahithReddy/Desktop/python/data.pt')
    employee_id = real_time_face_detection()
    # employee_name = data.get('emp_name')
    # status = data.get('status')
    print("employee_id is ---------------- ",employee_id)



    if employee_id is None:
        return jsonify({'messsage': 'emp_id and emp_name are required'}), 400
    if employee_id == 'Unknown':
        print("Inside if employee_id is unknown -------------------")
        return({'message':'Employee not found','image_path':image_path})

    emp_exists = Employee.query.filter_by(emp_id = employee_id).first()
    today_record = Attendance.query.filter_by(emp_id=employee_id,date=current_time.date() ).first()



    attendance_entry_exit = Attendance(emp_id=employee_id)
    attendance_entry_exit.mark_entry_exit()
    if emp_exists:
        if  today_record:
            # today_record.status = status

            db.session.commit()
            return({'message':'Your exit time has been updated','image_path':image_path})

        else:

            return({'message':'Your attendance has been marked','image_path':image_path})

    else:
        return({'message':'Employee not found','image_path':image_path})

    # return jsonify({'message': 'Entry/Exit marked successfully'}), 200

@app.route('/attendance', methods=['POST'])
def update_attendance():
    current_time = datetime.utcnow()
    data = request.json
    # image_data = base64.b64decode(image_path)
    # print("image_path is -------",image_path)
    # employee_id = face_match('C:/Users/SahithReddy/Desktop/python/src/assets/captured_image.jpg','C:/Users/SahithReddy/Desktop/python/data.pt')
    employee_id = data.get('emp_id')
    employee_name = data.get('emp_name')
    status = data.get('status')
    print("employee_id is ---------------- ",employee_id)



    if employee_id is None:
        return jsonify({'messsage': 'emp_id is required'}), 400

    employee = Employee.query.filter_by(emp_id=employee_id).first()



    if employee:
        today_record = Attendance.query.filter_by(emp_id=employee_id, date=datetime.utcnow().date()).first()

        if today_record:
            today_record.status = status
            db.session.commit()
            return jsonify({'message': 'Attendance updated successfully'})
        else:
            return jsonify({'message': 'No attendance record found for today'})
    else:
        return jsonify({'message': 'Employee not found'})




@app.route('/attendance',methods=['GET'])
@cross_origin()
def get_attendance():

    attendances = Attendance.query.filter_by(date = datetime.utcnow().date())
    return jsonify([attendance.serialize() for attendance in attendances])

UPLOAD_FOLDER = 'D:/mainbranch/Smart-Airport-template/src/assets/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/attendance/upload_image', methods=['POST'])
@cross_origin()
def upload_image():
    # employee_id = real_time_face_detection()
    if 'image' not in request.files:
        return jsonify({'message': 'No image received'}), 400

    image = request.files['image']


    print("image is :::::::::::::",image)

    if image.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if image and allowed_file(image.filename):
        image_data = image.read()
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'captured_image.jpg')
        with open(image_path, 'wb') as f:
            f.write(image_data)
            # employee_id =  face_match('C:/Users/SahithReddy/Desktop/python/src/assets/captured_image.jpg','C:/Users/SahithReddy/Desktop/python/data.pt')
            # employee_id = real_time_face_detection()
            # print(employee_id)
            # if employee_id is None:
            #   return jsonify({'messsage': 'emp_id and emp_name are required'}), 400
            # if employee_id == 'Unknown':
            #   print("Inside if employee_id is unknown -------------------")
            #   return({'message':'Employee not found','image_path':image_path})
            # print("Employee id is ---------------------------------------",employee_id)

            # emp_exists = Employee.query.filter_by(emp_id = employee_id).first()
            # today_record = Attendance.query.filter_by(emp_id=employee_id,date=datetime.now().date() ).first()



            # attendance_entry_exit = Attendance(emp_id=employee_id)
            # attendance_entry_exit.mark_entry_exit()
            # if emp_exists:
            #     if  today_record:
            #         # today_record.status = status

            #         db.session.commit()
            #         return({'message':'Your exit time has been updated','image_path':image_path})

            #     else:

            #         return({'message':'Your attendance has been marked','image_path':image_path})

            # else:
            #     return({'message':'Employee not found','image_path':image_path})


        return jsonify({'message': 'Image saved successfully','image_path':image_path}), 200
    else:
        return jsonify({'message': 'Invalid file type'}), 400

@app.route('/recognize',methods=['POST'])
@cross_origin()
def recognize():
    employee_id =  face_match('C:/Users/SunilPradhan/Desktop/Airport AMS/images/captured_image/captured_image.jpg','C:/Users/SunilPradhan/Desktop/Airport AMS/backendFlask/data.pt')
    print("----------------------------employee ID is ::::::;",employee_id)
    # employee_id = real_time_face_detection()
    print(employee_id)
    emp_name = Employee.query
    if employee_id is None:
      return jsonify({'messsage': 'emp_id and emp_name are required'}), 400
    if employee_id == 'Unknown':
      print("Inside if employee_id is unknown -------------------", employee_id)
      return {'message':'Employee not found', 'emp_id': 'unknown'}
    print("Employee id is ---------------------------------------",employee_id)

    emp_exists = Employee.query.filter_by(emp_id = employee_id).first()
    today_record = Attendance.query.filter_by(emp_id=employee_id,date=datetime.now().date() ).first()



    attendance_entry_exit = Attendance(emp_id=employee_id)
    attendance_entry_exit.mark_entry_exit()
    if emp_exists:
        if  today_record:
            # today_record.status = status

            db.session.commit()
            empname = emp_exists.emp_name
            print("emp_name i s==================",emp_exists)
            return {'message':'Thank You.Your exit time has been updated','emp_id': empname}

        else:
            empname = emp_exists.emp_name
            return {'message':'Thank You.Your attendance has been marked', 'emp_id': empname}

    else:
        return({'message':'Employee not found'})




def allow_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload_image', methods=['POST'])
@cross_origin()
def post_image():
    image = request.files['image']
    emp_id = request.form['emp_id']
    print('YAAY empid is :::::::::::::::::',emp_id)

    print("Data is  -------------------",image)
    # Destiny = os.makedirs(f'D:/database/frontend/Face-Recognition-frontend/src/assets/{emp_id}')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # app.config['folder'] = Destiny
    # print(app.config['folder'])

    if 'image' not in request.files:
        return jsonify({'message': 'No image received'}), 400


    # image = request.files['image']

    if image.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    folder_path = os.path.join('D:/database/frontend/Face-Recognition-frontend/src/assets/', emp_id)
    os.makedirs(folder_path, exist_ok=True)

    if image and allow_file(image.filename):
        image_data = image.read()
        image_path = os.path.join(folder_path, 'captured_image.jpg')
        with open(image_path, 'wb') as f:
            f.write(image_data)
            # employee_id = face_match(image_path,data_path = 'D:/database/frontend/Face-Recognition-frontend/data.pt')
            # print(employee_id)



        return jsonify({'message': 'Image saved successfully','image_path':image_path}), 200
    else:
        return jsonify({'message': 'Invalid file type'}), 400




class Timeoff(db.Model):
    timeoff_id = db.Column(db.Integer,primary_key = True,autoincrement = True)
    emp_id = db.Column(db.String(100),nullable = False)
    emp_name = db.Column(db.String(120),nullable = False)
    timeoff = db.Column(db.String(120),nullable = False)
    date = db.Column(db.DateTime,nullable = False)
    dayoftheweek = db.Column(db.String(20),nullable = False)
    type = db.Column(db.String(120),nullable = False)
    unitoftime = db.Column(db.String(120),nullable = False)
    comment = db.Column(db.String(120))

    def serialize(self):
        return {
            'timeoff_id':self.timeoff_id,
            'timeoff':self.timeoff,
            'date':self.date,
            'dayoftheweek':self.dayoftheweek,
            'type':self.type,
            'unitoftime':self.unitoftime,
            'comment':self.comment
        }

@app.route('/timeoff/<int:emp_id>',methods = ['GET'])
@cross_origin()
def get_timeoff(emp_id):
    timeoffs = Timeoff.query.filter_by(emp_id = emp_id).all()
    return jsonify([i.serialize() for i in timeoffs])

class holi(db.Model):
    id = db.Column(db.Integer, autoincrement = True)
    holiday_date = db.Column(db.String(255))
    title = db.Column(db.String(255),primary_key=True)

    def __init__(self, holiday_date, title):
        self.holiday_date = holiday_date
        self.title = title

with app.app_context():
    db.create_all()
    if not holi.query.filter_by(holiday_date='2024-01-01').first():
      sample_data = [
          holi(holiday_date='2024-01-01', title="New Year's Day"),
          holi(holiday_date='2024-15-01', title="Sankranti / Pongal"),
          holi(holiday_date='2024-26-01', title="Republic Day"),
          holi(holiday_date='2024-18-02', title="Mahashivratri"),
          holi(holiday_date='2024-07-04', title="Good Friday"),
          holi(holiday_date='2024-22-04', title="Eid-Ul-Fitr"),
          holi(holiday_date='2024-01-05', title="May Day"),
          holi(holiday_date='2024-29-06', title="Bakra Id"),
          holi(holiday_date='2024-15-08', title="Independence Day"),
          holi(holiday_date='2024-19-09', title="Ganesh Chathurthi"),
          holi(holiday_date='2024-02-10', title="Gandhi Jayanti"),
          holi(holiday_date='2024-24-10', title="Dusshera"),
          holi(holiday_date='2024-12-11', title="Diwali"),
          holi(holiday_date='2024-13-11', title="Balipadyami Diwali / Govardhan Pooja"),
          holi(holiday_date='2024-25-12', title="Christmas"),
          ]

      for data in sample_data:
          db.session.add(data)

      db.session.commit()

@app.route('/holiday', methods=['GET'])
def get_all_data():
    data = holi.query.all()
    data_list = []

    for item in data:
        data_list.append({
            'id': item.id,
            'date': item.holiday_date,
            'title': item.title
        })

    return data_list

# @app.route('/face_recognization/<string: image>',methods = ['POST'])
# @cross_origin()
# def face_recognization(image):
#     name = real_time_face_detection(image)




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

    # print(employee_id('abcd'))


