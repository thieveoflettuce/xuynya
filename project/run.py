import sys
import os

# Добавим путь к корневой директории, чтобы Python "увидел" папку app/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import create_app, db
    from app.models import create_triggers
except ImportError as e:
    print("ERROR: Не удалось импортировать необходимые модули.")
    print("Убедитесь, что все зависимости установлены:")
    print("pip install flask flask_sqlalchemy flask_bcrypt flask_jwt_extended flask_migrate flask_cors")
    print("Подробности:", e)
    sys.exit(1)

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            create_triggers()
            print("База данных и триггеры успешно инициализированы.")
        except Exception as e:
            print(f"ОШИБКА при создании базы данных или триггеров: {e}")
            sys.exit(1)

    print("Запуск Flask-приложения на http://0.0.0.0:5000/")
    app.run(debug=True, host='0.0.0.0')
