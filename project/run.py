from app import create_app, db
from app.models import User, Course, Module, Enrollment, Assessment, Feedback

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц
    app.run(debug=True)
