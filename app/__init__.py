from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
import os
import click
from flask.cli import with_appcontext

# Инициализация объектов
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Конфигурация
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # Токен действителен 24 часа
    app.config['UPLOAD_FOLDER'] = 'uploads'  # Папка для загрузки файлов

    # Инициализация
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)  # Включаем поддержку CORS для всех маршрутов

    # Регистрация маршрутов
    from .auth import auth_bp
    from .courses import course_bp
    from .notifications import notification_bp
    from .attachments import attachment_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(course_bp, url_prefix='/api')
    app.register_blueprint(notification_bp, url_prefix='/api')
    app.register_blueprint(attachment_bp, url_prefix='/api')

    # Добавляем обработку ошибок
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'message': 'Internal server error'}, 500

    # Добавляем CLI команду для инициализации базы данных
    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        """Инициализация базы данных."""
        from .models import create_triggers
        
        # Убедимся, что instance директория существует
        os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)
        
        # Создание таблиц
        db.create_all()
        
        # Создание триггеров
        try:
            create_triggers()
            click.echo('База данных и триггеры успешно инициализированы.')
        except Exception as e:
            click.echo(f'Ошибка при создании триггеров: {e}')
    
    app.cli.add_command(init_db_command)
    
    return app
