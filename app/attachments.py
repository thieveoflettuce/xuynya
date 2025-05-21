from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from .models import db, Module, Attachment, Notification

attachment_bp = Blueprint('attachments', __name__)

# Допустимые типы файлов
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Получение вложений для модуля
@attachment_bp.route('/modules/<int:module_id>/attachments', methods=['GET'])
def get_module_attachments(module_id):
    attachments = Attachment.get_module_attachments(module_id)
    result = [{
        'id': attachment.id,
        'module_id': attachment.module_id,
        'filename': attachment.filename,
        'file_path': attachment.file_path,
        'file_type': attachment.file_type,
        'file_size': attachment.file_size,
        'uploaded_at': attachment.uploaded_at.isoformat()
    } for attachment in attachments]

    return jsonify(result)

# Получение вложений для курса
@attachment_bp.route('/courses/<int:course_id>/attachments', methods=['GET'])
def get_course_attachments(course_id):
    attachments = Attachment.get_course_attachments(course_id)
    result = [{
        'id': attachment.id,
        'module_id': attachment.module_id,
        'module_title': attachment.module.title,
        'filename': attachment.filename,
        'file_path': attachment.file_path,
        'file_type': attachment.file_type,
        'file_size': attachment.file_size,
        'uploaded_at': attachment.uploaded_at.isoformat()
    } for attachment in attachments]

    return jsonify(result)

# Загрузка вложения
@attachment_bp.route('/modules/<int:module_id>/attachments', methods=['POST'])
@jwt_required()
def upload_attachment(module_id):
    # Проверка существования модуля
    module = Module.query.get_or_404(module_id)

    if 'file' not in request.files:
        return jsonify({'message': 'Файл не найден в запросе'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Не выбран файл'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Недопустимый тип файла'}), 400

    # Создание директории для загрузки, если ее нет
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), f'module_{module_id}')
    os.makedirs(upload_dir, exist_ok=True)

    # Сохранение файла
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)

    # Определение типа файла и размера
    file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    file_size = os.path.getsize(file_path)

    # Относительный путь для сохранения в базе данных
    relative_path = os.path.join(f'module_{module_id}', unique_filename)

    # Создание записи в базе данных
    try:
        attachment = Attachment(
            module_id=module_id,
            filename=filename,
            file_path=relative_path,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(attachment)

        # Создание уведомлений для всех пользователей, зарегистрированных на курс
        from .models import Enrollment, Notification
        enrollments = Enrollment.query.filter_by(course_id=module.course_id).all()
        for enrollment in enrollments:
            notification = Notification(
                user_id=enrollment.user_id,
                title='Новое вложение в модуле',
                message=f'В модуль {module.title} курса {module.course.title} добавлено новое вложение: {filename}',
                is_read=False
            )
            db.session.add(notification)

        db.session.commit()

        return jsonify({
            'message': 'Файл успешно загружен',
            'attachment_id': attachment.id,
            'filename': filename,
            'file_path': relative_path
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Ошибка при загрузке файла: {str(e)}'}), 500

# Удаление вложения
@attachment_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)

    try:
        # Удаление файла с диска
        file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), attachment.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Удаление записи из базы данных
        db.session.delete(attachment)
        db.session.commit()

        return jsonify({'message': 'Вложение успешно удалено'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Ошибка при удалении вложения: {str(e)}'}), 500

# Получение статистики по вложениям для модулей
@attachment_bp.route('/modules/attachment-statistics', methods=['GET'])
@jwt_required()
def get_module_attachment_statistics():
    # Запрос с вычисляемыми полями:
    # 1. Количество вложений
    # 2. Суммарный размер вложений
    # 3. Средний размер вложения

    module_stats = db.session.query(
        Module.id.label('module_id'),
        Module.title.label('module_title'),
        db.func.count(Attachment.id).label('attachment_count'),
        db.func.sum(Attachment.file_size).label('total_size'),
        (db.func.sum(Attachment.file_size) / (1024.0 * 1024.0)).label('total_size_mb'),
        (db.func.avg(Attachment.file_size) / 1024.0).label('avg_size_kb')
    ).outerjoin(
        Attachment, Module.id == Attachment.module_id
    ).group_by(
        Module.id, Module.title
    ).having(
        db.func.count(Attachment.id) > 0
    ).order_by(
        db.func.count(Attachment.id).desc()
    ).all()

    result = [{
        'module_id': stat.module_id,
        'module_title': stat.module_title,
        'attachment_count': stat.attachment_count,
        'total_size': stat.total_size,
        'total_size_mb': round(float(stat.total_size_mb), 2) if stat.total_size_mb else 0,
        'avg_size_kb': round(float(stat.avg_size_kb), 2) if stat.avg_size_kb else 0
    } for stat in module_stats]

    return jsonify(result)
