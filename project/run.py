try:
    from app import create_app, db
    from app.models import User, Course, Module, Enrollment, Assessment, Feedback, create_triggers
except ImportError:
    print("ERROR: Не удалось импортировать необходимые модули.")
    print("Убедитесь, что все зависимости установлены:")
    print("pip install flask flask_sqlalchemy flask_bcrypt flask_jwt_extended flask_migrate")
    import sys
    sys.exit(1)

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()  # Создание таблиц
            create_triggers()  # Создание триггеров
            print("База данных успешно инициализирована")
            print("Триггеры успешно созданы")
        except Exception as e:
            print(f"ОШИБКА при создании базы данных: {e}")
            sys.exit(1)

    print("Запуск Flask-приложения на http://0.0.0.0:5000/")
    app.run(debug=True, host='0.0.0.0')
