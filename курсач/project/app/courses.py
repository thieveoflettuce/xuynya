from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Course, Module, Enrollment, Assessment, Feedback

course_bp = Blueprint('courses', __name__)

# ========== Курсы (Courses) ==========

# Получение всех курсов
@course_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    result = [{'id': course.id, 'title': course.title, 'description': course.description} for course in courses]
    return jsonify(result)

# Получение конкретного курса
@course_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    modules = [{'id': module.id, 'title': module.title} for module in course.modules]

    # Вычисляем средний рейтинг курса с помощью нашей функции
    avg_rating = course.calculate_avg_rating()

    result = {
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'modules': modules,
        'average_rating': avg_rating,
        'enrollment_count': len(course.enrollments)
    }

    return jsonify(result)

# Создание нового курса
@course_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    current_user = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({'message': 'Missing required field: title'}), 400

    course = Course(title=title, description=description)
    db.session.add(course)
    db.session.commit()

    return jsonify({
        'message': 'Course created successfully',
        'course_id': course.id
    }), 201

# Обновление курса
@course_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()

    if 'title' in data:
        course.title = data['title']

    if 'description' in data:
        course.description = data['description']

    db.session.commit()

    return jsonify({'message': 'Course updated successfully'})

# Удаление курса
@course_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()

    return jsonify({'message': 'Course deleted successfully'})

# Получение популярных курсов (реализация запроса 2)
@course_bp.route('/courses/popular', methods=['GET'])
def get_popular_courses():
    popular_courses = Course.get_popular_courses()

    result = [{
        'course_id': course.course_id,
        'course_title': course.course_title,
        'enrollment_count': course.enrollment_count,
        'average_rating': float(course.average_rating) if course.average_rating else 0
    } for course in popular_courses]

    return jsonify(result)

# Получение статистики по курсам (реализация запроса 5)
@course_bp.route('/courses/statistics', methods=['GET'])
@jwt_required()
def get_course_statistics():
    statistics = Course.get_course_statistics()

    result = [{
        'course_id': stat.course_id,
        'course_title': stat.course_title,
        'module_count': stat.module_count,
        'student_count': stat.student_count,
        'enrollment_percentage': float(stat.enrollment_percentage) if stat.enrollment_percentage else 0,
        'average_rating': float(stat.average_rating) if stat.average_rating else 0,
        'satisfaction_percentage': float(stat.satisfaction_percentage) if stat.satisfaction_percentage else 0
    } for stat in statistics]

    return jsonify(result)

# Получение статистики по модулям курсов (реализация запроса 3)
@course_bp.route('/courses/module-statistics', methods=['GET'])
@jwt_required()
def get_course_module_statistics():
    statistics = Course.get_course_module_statistics()

    result = [{
        'course_id': stat.course_id,
        'course_title': stat.course_title,
        'module_count': stat.module_count,
        'assessment_count': stat.assessment_count,
        'average_grade': float(stat.average_grade) if stat.average_grade else 0
    } for stat in statistics]

    return jsonify(result)

# ========== Модули (Modules) ==========

# Получение модулей курса
@course_bp.route('/courses/<int:course_id>/modules', methods=['GET'])
def get_modules(course_id):
    modules = Module.query.filter_by(course_id=course_id).all()
    result = [{
        'id': module.id,
        'title': module.title,
        'content': module.content
    } for module in modules]

    return jsonify(result)

# Получение конкретного модуля
@course_bp.route('/modules/<int:module_id>', methods=['GET'])
def get_module(module_id):
    module = Module.query.get_or_404(module_id)
    result = {
        'id': module.id,
        'course_id': module.course_id,
        'title': module.title,
        'content': module.content
    }

    return jsonify(result)

# Создание нового модуля
@course_bp.route('/courses/<int:course_id>/modules', methods=['POST'])
@jwt_required()
def create_module(course_id):
    Course.query.get_or_404(course_id)  # Проверка существования курса

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Missing required fields'}), 400

    module = Module(course_id=course_id, title=title, content=content)
    db.session.add(module)
    db.session.commit()

    return jsonify({
        'message': 'Module created successfully',
        'module_id': module.id
    }), 201

# Обновление модуля
@course_bp.route('/modules/<int:module_id>', methods=['PUT'])
@jwt_required()
def update_module(module_id):
    module = Module.query.get_or_404(module_id)
    data = request.get_json()

    if 'title' in data:
        module.title = data['title']

    if 'content' in data:
        module.content = data['content']

    db.session.commit()

    return jsonify({'message': 'Module updated successfully'})

# Удаление модуля
@course_bp.route('/modules/<int:module_id>', methods=['DELETE'])
@jwt_required()
def delete_module(module_id):
    module = Module.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()

    return jsonify({'message': 'Module deleted successfully'})

# ========== Регистрация на курсы (Enrollments) ==========

# Регистрация пользователя на курс
@course_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(course_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']

    try:
        enrollment = Enrollment.enroll_user_in_course(user_id, course_id)
        return jsonify({
            'message': 'Successfully enrolled in the course',
            'enrollment_id': enrollment.id
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

# Получение курсов пользователя
@course_bp.route('/enrollments', methods=['GET'])
@jwt_required()
def get_user_enrollments():
    current_user = get_jwt_identity()
    user_id = current_user['id']

    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    result = [{
        'id': enrollment.id,
        'course_id': enrollment.course_id,
        'course_title': enrollment.course.title,
        'progress': enrollment.progress,
        'enrollment_date': enrollment.enrollment_date.isoformat()
    } for enrollment in enrollments]

    return jsonify(result)

# Отмена регистрации на курс
@course_bp.route('/courses/<int:course_id>/unenroll', methods=['DELETE'])
@jwt_required()
def unenroll_course(course_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']

    enrollment = Enrollment.query.filter_by(
        user_id=user_id, course_id=course_id).first_or_404()

    db.session.delete(enrollment)
    db.session.commit()

    return jsonify({'message': 'Successfully unenrolled from the course'})

# Обновление прогресса пользователя
@course_bp.route('/courses/<int:course_id>/progress', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']

    try:
        # Используем нашу функцию для расчета прогресса
        progress = Enrollment.calculate_user_progress(user_id, course_id)

        # Также обновляем запись о прогрессе в базе данных
        Enrollment.update_user_progress(user_id, course_id)

        return jsonify({'progress': progress})
    except ValueError as e:
        return jsonify({'message': str(e)}), 404

# ========== Оценки (Assessments) ==========

# Получение оценок пользователя
@course_bp.route('/assessments', methods=['GET'])
@jwt_required()
def get_user_assessments():
    current_user = get_jwt_identity()
    user_id = current_user['id']

    assessments = Assessment.query.filter_by(user_id=user_id).all()
    result = [{
        'id': assessment.id,
        'module_id': assessment.module_id,
        'module_title': assessment.module.title,
        'course_id': assessment.module.course_id,
        'course_title': assessment.module.course.title,
        'grade': assessment.grade,
        'assessment_date': assessment.assessment_date.isoformat()
    } for assessment in assessments]

    return jsonify(result)

# Создание или обновление оценки
@course_bp.route('/modules/<int:module_id>/assessment', methods=['POST'])
@jwt_required()
def save_assessment(module_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']
    data = request.get_json()

    if 'grade' not in data:
        return jsonify({'message': 'Missing required field: grade'}), 400

    grade = float(data['grade'])
    if grade < 0 or grade > 5:
        return jsonify({'message': 'Grade must be between 0 and 5'}), 400

    # Получение или создание оценки
    assessment = Assessment.get_or_create(user_id, module_id)

    # Сохранение оценки (также обновляет прогресс пользователя через триггер)
    assessment.save_grade(grade)

    return jsonify({'message': 'Assessment saved successfully'})

# ========== Отзывы (Feedbacks) ==========

# Получение отзывов о курсе
@course_bp.route('/courses/<int:course_id>/feedbacks', methods=['GET'])
def get_course_feedbacks(course_id):
    feedbacks = Feedback.query.filter_by(course_id=course_id).all()
    result = [{
        'id': feedback.id,
        'user_id': feedback.user_id,
        'user_name': feedback.user.name,
        'comment': feedback.comment,
        'rating': feedback.rating,
        'created_at': feedback.created_at.isoformat()
    } for feedback in feedbacks]

    return jsonify(result)

# Создание отзыва
@course_bp.route('/courses/<int:course_id>/feedback', methods=['POST'])
@jwt_required()
def create_feedback(course_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']
    data = request.get_json()

    if 'rating' not in data:
        return jsonify({'message': 'Missing required field: rating'}), 400

    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400

    comment = data.get('comment', '')

    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_feedback = Feedback.query.filter_by(
        user_id=user_id, course_id=course_id).first()

    if existing_feedback:
        # Обновляем существующий отзыв
        existing_feedback.rating = rating
        existing_feedback.comment = comment
        db.session.commit()
        return jsonify({'message': 'Feedback updated successfully'})
    else:
        # Создаем новый отзыв
        feedback = Feedback(user_id=user_id, course_id=course_id, rating=rating, comment=comment)
        db.session.add(feedback)
        db.session.commit()
        return jsonify({
            'message': 'Feedback created successfully',
            'feedback_id': feedback.id
        }), 201

# Удаление отзыва
@course_bp.route('/feedbacks/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(feedback_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']

    feedback = Feedback.query.get_or_404(feedback_id)

    # Проверяем, принадлежит ли отзыв текущему пользователю
    if feedback.user_id != user_id:
        return jsonify({'message': 'Unauthorized to delete this feedback'}), 403

    db.session.delete(feedback)
    db.session.commit()

    return jsonify({'message': 'Feedback deleted successfully'})

# ========== Статистика (Statistics) ==========

# Получение статистики успеваемости пользователей (реализация запроса 4)
@course_bp.route('/statistics/user-performance', methods=['GET'])
@jwt_required()
def get_user_performance_statistics():
    statistics = User.get_user_performance_statistics()

    result = [{
        'user_id': stat.user_id,
        'user_name': stat.user_name,
        'completed_assessments': stat.completed_assessments,
        'average_grade': float(stat.average_grade) if stat.average_grade else 0,
        'performance_percentage': float(stat.performance_percentage) if stat.performance_percentage else 0,
        'performance_category': stat.performance_category
    } for stat in statistics]

    return jsonify(result)

# Получение статистики активности пользователей (реализация запроса 6)
@course_bp.route('/statistics/user-activity', methods=['GET'])
@jwt_required()
def get_user_activity_statistics():
    statistics = User.get_user_activity_statistics()

    result = [{
        'user_id': stat.user_id,
        'user_name': stat.user_name,
        'enrolled_courses': stat.enrolled_courses,
        'completed_assessments': stat.completed_assessments,
        'completion_rate': float(stat.completion_rate) if stat.completion_rate else 0,
        'average_progress': float(stat.average_progress) if stat.average_progress else 0,
        'average_feedback': float(stat.average_feedback) if stat.average_feedback else 0
    } for stat in statistics]

    return jsonify(result)

# Получение активных пользователей с курсами (реализация запроса 1)
@course_bp.route('/statistics/active-users', methods=['GET'])
@jwt_required()
def get_active_users_with_courses():
    statistics = User.get_active_users_with_courses()

    result = [{
        'user_id': stat.user_id,
        'user_name': stat.user_name,
        'email': stat.email,
        'enrolled_courses': stat.enrolled_courses,
        'last_enrollment_date': stat.last_enrollment_date.isoformat() if stat.last_enrollment_date else None
    } for stat in statistics]

    return jsonify(result)
