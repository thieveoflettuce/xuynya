from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')

    enrollments = db.relationship('Enrollment', back_populates='user')
    assessments = db.relationship('Assessment', back_populates='user')
    feedbacks = db.relationship('Feedback', back_populates='user')

    def __repr__(self):
        return f'<User {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    modules = db.relationship('Module', back_populates='course')
    enrollments = db.relationship('Enrollment', back_populates='course')
    feedbacks = db.relationship('Feedback', back_populates='course')

    def __repr__(self):
        return f'<Course {self.title}>'

class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    course = db.relationship('Course', back_populates='modules')
    assessments = db.relationship('Assessment', back_populates='module')

    def __repr__(self):
        return f'<Module {self.title}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)

    user = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment {self.user_id} - {self.course_id}>'

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grade = db.Column(db.Float, nullable=False)

    module = db.relationship('Module', back_populates='assessments')
    user = db.relationship('User', back_populates='assessments')

    def __repr__(self):
        return f'<Assessment {self.grade} for user {self.user_id}>'

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=False)

    course = db.relationship('Course', back_populates='feedbacks')
    user = db.relationship('User', back_populates='feedbacks')

    def __repr__(self):
        return f'<Feedback for course {self.course_id} by user {self.user_id}>'
