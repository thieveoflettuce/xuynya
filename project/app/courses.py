from flask import Blueprint, request, jsonify
from .models import db, Course, Module

course_bp = Blueprint('courses', __name__)

# Получение всех курсов
@course_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{'id': course.id, 'title': course.title} for course in courses])

# Создание нового курса
@course_bp.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title or not description:
        return jsonify({'message': 'Missing required fields'}), 400

    course = Course(title=title, description=description)
    db.session.add(course)
    db.session.commit()

    return jsonify({'message': 'Course created successfully', 'course_id': course.id}), 201
