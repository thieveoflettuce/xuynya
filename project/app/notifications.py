from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, User, Notification

notification_bp = Blueprint('notifications', __name__)

# Получение уведомлений пользователя
@notification_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    current_user = get_jwt_identity()
    user_id = current_user['id']

    # Параметр для фильтрации только непрочитанных уведомлений
    unread_only = request.args.get('unread', 'false').lower() == 'true'

    notifications = Notification.get_user_notifications(user_id, unread_only)
    result = [{
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat()
    } for notification in notifications]

    return jsonify(result)

# Получение количества непрочитанных уведомлений
@notification_bp.route('/notifications/count', methods=['GET'])
@jwt_required()
def get_unread_notification_count():
    current_user = get_jwt_identity()
    user_id = current_user['id']

    count = db.session.query(db.func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar() or 0

    return jsonify({'unread_count': count})

# Отметка уведомления как прочитанного
@notification_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notification_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']

    notification = Notification.query.get_or_404(notification_id)

    # Проверка, принадлежит ли уведомление текущему пользователю
    if notification.user_id != user_id:
        return jsonify({'message': 'Нет прав на редактирование этого уведомления'}), 403

    notification.mark_as_read()

    return jsonify({'message': 'Уведомление отмечено как прочитанное'})

# Отметка всех уведомлений пользователя как прочитанных
@notification_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_as_read():
    current_user = get_jwt_identity()
    user_id = current_user['id']

    notifications = Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.session.commit()

    return jsonify({'message': 'Все уведомления отмечены как прочитанные'})

# Удаление уведомления
@notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    current_user = get_jwt_identity()
    user_id = current_user['id']

    notification = Notification.query.get_or_404(notification_id)

    # Проверка, принадлежит ли уведомление текущему пользователю
    if notification.user_id != user_id:
        return jsonify({'message': 'Нет прав на удаление этого уведомления'}), 403

    db.session.delete(notification)
    db.session.commit()

    return jsonify({'message': 'Уведомление успешно удалено'})

# Создание уведомления для пользователя (только для администраторов)
@notification_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    current_user = get_jwt_identity()
    creator_id = current_user['id']

    # Проверка прав (администратор)
    creator = User.query.get(creator_id)
    if not creator or creator.role != 'admin':
        return jsonify({'message': 'Нет прав на создание уведомлений'}), 403

    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    message = data.get('message')

    if not user_id or not title or not message:
        return jsonify({'message': 'Не указаны обязательные поля'}), 400

    # Проверка существования пользователя
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': f'Пользователь с ID {user_id} не найден'}), 404

    notification = Notification.create_notification(user_id, title, message)

    return jsonify({
        'message': 'Уведомление успешно создано',
        'notification_id': notification.id
    }), 201

# Получение статистики по уведомлениям пользователей
@notification_bp.route('/notifications/statistics', methods=['GET'])
@jwt_required()
def get_notification_statistics():
    current_user = get_jwt_identity()
    user_id = current_user['id']

    # Проверка прав (администратор)
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'message': 'Нет прав на просмотр статистики уведомлений'}), 403

    # Запрос с вычисляемыми полями:
    # 1. Общее количество уведомлений пользователя
    # 2. Количество непрочитанных уведомлений
    # 3. Процент прочитанных уведомлений

    user_stats = db.session.query(
        User.id.label('user_id'),
        User.name.label('user_name'),
        User.email.label('user_email'),
        db.func.count(Notification.id).label('total_notifications'),
        db.func.sum(db.case([(Notification.is_read == False, 1)], else_=0)).label('unread_notifications'),
        (db.func.sum(db.case([(Notification.is_read == True, 1)], else_=0)) * 100.0 /
         db.func.nullif(db.func.count(Notification.id), 0)).label('read_percentage')
    ).outerjoin(
        Notification, User.id == Notification.user_id
    ).group_by(
        User.id, User.name, User.email
    ).having(
        db.func.count(Notification.id) > 0
    ).order_by(
        db.func.count(Notification.id).desc()
    ).all()

    result = [{
        'user_id': stat.user_id,
        'user_name': stat.user_name,
        'user_email': stat.user_email,
        'total_notifications': stat.total_notifications,
        'unread_notifications': stat.unread_notifications or 0,
        'read_percentage': round(float(stat.read_percentage), 2) if stat.read_percentage else 0
    } for stat in user_stats]

    return jsonify(result)
