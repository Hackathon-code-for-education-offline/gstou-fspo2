# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

hello = 'hello'

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
db = SQLAlchemy(app)

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculties = db.relationship('Faculty', backref='university', lazy=True)
    chats = db.relationship('Chat', backref='university', lazy=True)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    departments = db.relationship('Department', backref='faculty', lazy=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    courses = db.relationship('Course', backref='department', lazy=True)



class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20))
    enrollment_date = db.Column(db.DateTime, nullable=False)
    chats = db.relationship('Chat', secondary='student_chat', backref='students')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20))
    chats = db.relationship('Chat', backref='professor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# Then, define the Course class
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    students = db.relationship('Student', secondary='enrollments', backref='courses')
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'))
    professor = db.relationship('Professor', backref='courses')
    schedule = db.Column(db.String(100))
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participants = db.Column(db.String(1000), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(1000), nullable=False)

class StudentChat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    content = db.Column(db.String(1000), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_type = data.get('user_type')

    if user_type == 'student':
        full_name = data.get('full_name')
        username = data.get('username')
        phone_number = data.get('phone_number')
        password = data.get('password')
        enrollment_date = data.get('enrollment_date')

        if not full_name or not username or not phone_number or not password or not enrollment_date:
            return jsonify({'error': 'Incomplete data provided'}), 400

        username = username.lower().replace(' ', '')

        if Student.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        new_student = Student(full_name=full_name, username=username)
        new_student.set_password(password)
        new_student.phone_number = phone_number
        new_student.enrollment_date = enrollment_date

        db.session.add(new_student)
        db.session.commit()

        student_data = {
            'id': new_student.id,
            'full_name': new_student.full_name,
            'username': new_student.username,
            'phone_number': new_student.phone_number,
            'enrollment_date': new_student.enrollment_date.strftime('%Y-%m-%d')
        }

        return jsonify({
            'message': 'Student registration successful',
            'user': student_data
        }), 201

    elif user_type == 'professor':
        full_name = data.get('full_name')
        username = data.get('username')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not full_name or not username or not phone_number or not password:
            return jsonify({'error': 'Incomplete data provided'}), 400

        username = username.lower().replace(' ', '')

        if Professor.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        new_professor = Professor(full_name=full_name, username=username)
        new_professor.set_password(password)
        new_professor.phone_number = phone_number

        db.session.add(new_professor)
        db.session.commit()

        professor_data = {
            'id': new_professor.id,
            'full_name': new_professor.full_name,
            'username': new_professor.username,
            'phone_number': new_professor.phone_number
        }

        return jsonify({
            'message': 'Professor registration successful',
            'user': professor_data
        }), 201

    elif user_type == 'university':
        name = data.get('name')

        if not name:
            return jsonify({'error': 'Incomplete data provided'}), 400

        if University.query.filter_by(name=name).first():
            return jsonify({'error': 'University already exists'}), 400

        new_university = University(name=name)

        # Creating a chat for the university
        university_chat = Chat(participants=json.dumps([name]), university_id=new_university.id)
        db.session.add(university_chat)
        db.session.commit()

        return jsonify({'message': 'University registration successful'}), 201

    elif user_type == 'faculty':
        name = data.get('name')
        university_name = data.get('university_name')

        if not name or not university_name:
            return jsonify({'error': 'Incomplete data provided'}), 400

        university = University.query.filter_by(name=university_name).first()
        if not university:
            return jsonify({'error': 'University not found'}), 404

        new_faculty = Faculty(name=name, university_id=university.id)

        db.session.add(new_faculty)
        db.session.commit()

        return jsonify({'message': 'Faculty registration successful'}), 201

    elif user_type == 'department':
        name = data.get('name')
        faculty_name = data.get('faculty_name')

        if not name or not faculty_name:
            return jsonify({'error': 'Incomplete data provided'}), 400

        faculty = Faculty.query.filter_by(name=faculty_name).first()
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404

        new_department = Department(name=name, faculty_id=faculty.id)

        db.session.add(new_department)
        db.session.commit()

        return jsonify({'message': 'Department registration successful'}), 201

    elif user_type == 'course':
        name = data.get('name')
        department_name = data.get('department_name')

        if not name or not department_name:
            return jsonify({'error': 'Incomplete data provided'}), 400

        department = Department.query.filter_by(name=department_name).first()
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        new_course = Course(name=name, department_id=department.id)

        db.session.add(new_course)
        db.session.commit()

        return jsonify({'message': 'Course registration successful'}), 201

    else:
        return jsonify({'error': 'Invalid user type'}), 400

@app.route('/create_chat', methods=['POST'])
def create_chat():
    data = request.get_json()
    participants = data.get('participants')
    university_name = data.get('university_name')

    if not participants or not university_name:
        return jsonify({'error': 'Participants or university name not provided'}), 400

    university = University.query.filter_by(name=university_name).first()
    if not university:
        return jsonify({'error': 'University not found'}), 404

    chat = Chat(participants=json.dumps(participants), university_id=university.id)
    db.session.add(chat)
    db.session.commit()

    return jsonify({'message': 'Chat created successfully', 'chat_id': chat.id}), 201

@app.route('/user/<int:user_id>/chats', methods=['GET'])
def get_user_chats(user_id):
    student = Student.query.get(user_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    user_chats = StudentChat.query.filter_by(student_id=user_id).all()
    chats_data = []

    for user_chat in user_chats:
        chat = Chat.query.get(user_chat.chat_id)
        participants = json.loads(chat.participants)
        chat_data = {
            'chat_id': chat.id,
            'participants': participants
        }
        chats_data.append(chat_data)

    return jsonify({'chats': chats_data}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
