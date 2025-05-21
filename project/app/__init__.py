try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_bcrypt import Bcrypt
    from flask_jwt_extended import JWTManager
    from flask_migrate import Migrate
except ImportError:
    print("ERROR: Отсутствуют необходимые зависимости.")
    print("Пожалуйста, установите следующие пакеты:")
    print("pip install flask flask-sqlalchemy flask-bcrypt flask-jwt-extended flask-migrate")
    import sys
    sys.exit(1)

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
