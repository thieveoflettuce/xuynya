from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from .config import Config

# Инициализация объектов
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)

    # Регистрация маршрутов
    from .auth import auth_bp
    from .courses import course_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(course_bp, url_prefix='/api')

    return app
