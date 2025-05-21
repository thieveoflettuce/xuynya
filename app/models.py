from datetime import datetime
from sqlalchemy import func, text, case
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = db.relationship('Enrollment', back_populates='user')
    assessments = db.relationship('Assessment', back_populates='user')
    feedbacks = db.relationship('Feedback', back_populates='user')
    notifications = db.relationship('Notification', back_populates='user')

    def __repr__(self):
        return f'<User {self.name}>'

    @classmethod
    def get_active_users_with_courses(cls):
        """Получить активных пользователей с информацией о курсах (реализация запроса 1)"""
        return db.session.query(
            cls.id.label('user_id'),
            cls.name.label('user_name'),
            cls.email,
            func.count(Enrollment.id).label('enrolled_courses'),
            func.max(Enrollment.enrollment_date).label('last_enrollment_date')
        ).join(
            Enrollment, cls.id == Enrollment.user_id
        ).filter(
            cls.role == 'student'
        ).group_by(
            cls.id, cls.name, cls.email
        ).having(
            func.count(Enrollment.id) > 0
        ).order_by(
            func.count(Enrollment.id).desc()
        ).all()

    @classmethod
    def get_user_performance_statistics(cls):
        """Получить статистику успеваемости пользователей (реализация запроса 4)"""
        query = db.session.query(
            cls.id.label('user_id'),
            cls.name.label('user_name'),
            func.count(Assessment.id).label('completed_assessments'),
            func.avg(Assessment.grade).label('average_grade'),
            (func.avg(Assessment.grade) / 5.0 * 100).label('performance_percentage'),
            case(
                [(func.avg(Assessment.grade) >= 4.5, 'Отлично'),
                 (func.avg(Assessment.grade) >= 3.5, 'Хорошо'),
                 (func.avg(Assessment.grade) >= 2.5, 'Удовлетворительно')],
                else_='Неудовлетворительно'
            ).label('performance_category')
        ).outerjoin(
            Assessment, cls.id == Assessment.user_id
        ).filter(
            cls.role == 'student'
        ).group_by(
            cls.id, cls.name
        ).order_by(
            func.avg(Assessment.grade).desc()
        )
        return query.all()

    @classmethod
    def get_user_activity_statistics(cls):
        """Получить статистику активности пользователей (реализация запроса 6)"""
        # Для реализации этого запроса может потребоваться написание raw SQL,
        # так как некоторые вычисления сложно представить через SQLAlchemy ORM

        # Используем текстовый SQL-запрос
        stmt = text("""
            SELECT
                u.id AS user_id,
                u.name AS user_name,
                COUNT(e.id) AS enrolled_courses,
                COUNT(a.id) AS completed_assessments,
                (COUNT(a.id) * 1.0 / NULLIF((SELECT COUNT(m.id) FROM modules m JOIN enrollments e2 ON m.course_id = e2.course_id WHERE e2.user_id = u.id), 0)) * 100 AS completion_rate,
                AVG(e.progress) AS average_progress,
                AVG(f.rating) AS average_feedback
            FROM
                users u
            LEFT JOIN
                enrollments e ON u.id = e.user_id
            LEFT JOIN
                assessments a ON u.id = a.user_id
            LEFT JOIN
                feedbacks f ON u.id = f.user_id
            WHERE
                u.role = 'student'
            GROUP BY
                u.id, u.name
            ORDER BY
                completion_rate DESC, average_progress DESC
        """)

        return db.session.execute(stmt).fetchall()

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    modules = db.relationship('Module', back_populates='course')
    enrollments = db.relationship('Enrollment', back_populates='course')
    feedbacks = db.relationship('Feedback', back_populates='course')

    def __repr__(self):
        return f'<Course {self.title}>'

    @classmethod
    def get_popular_courses(cls):
        """Получить популярные курсы (реализация запроса 2)"""
        return db.session.query(
            cls.id.label('course_id'),
            cls.title.label('course_title'),
            func.count(Enrollment.id).label('enrollment_count'),
            func.avg(Feedback.rating).label('average_rating')
        ).outerjoin(
            Enrollment, cls.id == Enrollment.course_id
        ).outerjoin(
            Feedback, cls.id == Feedback.course_id
        ).group_by(
            cls.id, cls.title
        ).having(
            func.count(Enrollment.id) >= 5,
            func.avg(Feedback.rating) > 3.5
        ).order_by(
            func.count(Enrollment.id).desc(),
            func.avg(Feedback.rating).desc()
        ).all()

    @classmethod
    def get_course_statistics(cls):
        """Получить статистику по курсам (реализация запроса 5)"""
        total_students = db.session.query(func.count(User.id)).filter(User.role == 'student').scalar() or 1

        return db.session.query(
            cls.id.label('course_id'),
            cls.title.label('course_title'),
            func.count(Module.id).label('module_count'),
            func.count(func.distinct(Enrollment.user_id)).label('student_count'),
            (func.count(func.distinct(Enrollment.user_id)) * 100.0 / total_students).label('enrollment_percentage'),
            func.avg(Feedback.rating).label('average_rating'),
            (func.avg(Feedback.rating) / 5.0 * 100).label('satisfaction_percentage')
        ).outerjoin(
            Module, cls.id == Module.course_id
        ).outerjoin(
            Enrollment, cls.id == Enrollment.course_id
        ).outerjoin(
            Feedback, cls.id == Feedback.course_id
        ).group_by(
            cls.id, cls.title
        ).order_by(
            func.count(func.distinct(Enrollment.user_id)).desc(),
            func.avg(Feedback.rating).desc()
        ).all()

    @classmethod
    def get_course_module_statistics(cls):
        """Получить статистику по модулям курсов (реализация запроса 3)"""
        year_ago = datetime.utcnow().replace(year=datetime.utcnow().year - 1)

        return db.session.query(
            cls.id.label('course_id'),
            cls.title.label('course_title'),
            func.count(Module.id).label('module_count'),
            func.count(Assessment.id).label('assessment_count'),
            func.avg(Assessment.grade).label('average_grade')
        ).outerjoin(
            Module, cls.id == Module.course_id
        ).outerjoin(
            Assessment, Module.id == Assessment.module_id
        ).filter(
            cls.created_at > year_ago
        ).group_by(
            cls.id, cls.title
        ).order_by(
            func.count(Module.id).desc(),
            func.avg(Assessment.grade).desc()
        ).all()

    def calculate_avg_rating(self):
        """Функция для вычисления среднего рейтинга курса (SQL-функция 1)"""
        result = db.session.query(func.avg(Feedback.rating)).filter(Feedback.course_id == self.id).scalar()
        return result or 0

class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = db.relationship('Course', back_populates='modules')
    assessments = db.relationship('Assessment', back_populates='module')
    attachments = db.relationship('Attachment', back_populates='module')

    def __repr__(self):
        return f'<Module {self.title}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course'),
    )

    def __repr__(self):
        return f'<Enrollment {self.user_id} - {self.course_id}>'

    @classmethod
    def enroll_user_in_course(cls, user_id, course_id):
        """Хранимая процедура для регистрации пользователя на курсе (SQL-процедура 1)"""
        # Проверка существования пользователя
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        # Проверка существования курса
        course = Course.query.get(course_id)
        if not course:
            raise ValueError(f"Курс с ID {course_id} не найден")

        # Проверка, не зарегистрирован ли пользователь уже на этот курс
        existing_enrollment = cls.query.filter_by(
            user_id=user_id, course_id=course_id).first()

        if existing_enrollment:
            raise ValueError("Пользователь уже зарегистрирован на этот курс")

        # Регистрация пользователя на курсе
        enrollment = cls(user_id=user_id, course_id=course_id, progress=0.0)
        db.session.add(enrollment)
        db.session.commit()

        return enrollment

    @staticmethod
    def calculate_user_progress(user_id, course_id):
        """Функция для вычисления прогресса пользователя по курсу (SQL-функция 2)"""
        # Подсчет общего количества модулей в курсе
        total_modules = db.session.query(func.count(Module.id)).\
            filter(Module.course_id == course_id).scalar() or 0

        # Подсчет количества выполненных модулей (имеющих оценки)
        completed_assessments = db.session.query(func.count(func.distinct(Assessment.module_id))).\
            join(Module, Assessment.module_id == Module.id).\
            filter(Assessment.user_id == user_id,
                Module.course_id == course_id,
                Assessment.grade > 0).scalar() or 0

        # Вычисление процента прогресса
        if total_modules > 0:
            progress_percentage = (completed_assessments / total_modules) * 100
        else:
            progress_percentage = 0

        return progress_percentage

    @classmethod
    def update_user_progress(cls, user_id, course_id):
        """Хранимая процедура для обновления прогресса пользователя по курсу (SQL-процедура 2)"""
        # Проверка наличия регистрации пользователя на курсе
        enrollment = cls.query.filter_by(
            user_id=user_id, course_id=course_id).first()

        if not enrollment:
            raise ValueError("Пользователь не зарегистрирован на этот курс")

        # Вычисление нового прогресса с использованием нашей функции
        new_progress = cls.calculate_user_progress(user_id, course_id)

        # Обновление записи о прогрессе
        enrollment.progress = new_progress
        enrollment.last_accessed = datetime.utcnow()
        db.session.commit()

        return enrollment

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grade = db.Column(db.Float, nullable=False, default=0.0)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)

    module = db.relationship('Module', back_populates='assessments')
    user = db.relationship('User', back_populates='assessments')

    def __repr__(self):
        return f'<Assessment {self.grade} for user {self.user_id}>'

    @staticmethod
    def get_or_create(user_id, module_id):
        """Получить или создать новую оценку за модуль"""
        assessment = Assessment.query.filter_by(
            user_id=user_id, module_id=module_id).first()

        if not assessment:
            assessment = Assessment(user_id=user_id, module_id=module_id, grade=0.0)
            db.session.add(assessment)
            db.session.commit()

        return assessment

    def save_grade(self, grade):
        """Сохранить оценку и обновить прогресс пользователя"""
        self.grade = grade
        self.assessment_date = datetime.utcnow()
        db.session.commit()

        # Получение курса, к которому принадлежит модуль
        course_id = self.module.course_id

        # Обновление прогресса пользователя
        try:
            Enrollment.update_user_progress(self.user_id, course_id)
        except ValueError:
            # Если пользователь не зарегистрирован на курс, регистрируем его
            Enrollment.enroll_user_in_course(self.user_id, course_id)
            # И снова обновляем прогресс
            Enrollment.update_user_progress(self.user_id, course_id)

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', back_populates='feedbacks')
    user = db.relationship('User', back_populates='feedbacks')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_feedback'),
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    def __repr__(self):
        return f'<Feedback for course {self.course_id} by user {self.user_id}>'

class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    module = db.relationship('Module', back_populates='attachments')

    def __repr__(self):
        return f'<Attachment {self.filename}>'

    @classmethod
    def get_module_attachments(cls, module_id):
        """Получить все вложения для конкретного модуля"""
        return cls.query.filter_by(module_id=module_id).all()

    @classmethod
    def get_course_attachments(cls, course_id):
        """Получить все вложения для конкретного курса"""
        return db.session.query(cls).\
            join(Module, cls.module_id == Module.id).\
            filter(Module.course_id == course_id).all()

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.title} for user {self.user_id}>'

    @classmethod
    def create_notification(cls, user_id, title, message):
        """Создать новое уведомление для пользователя"""
        notification = cls(user_id=user_id, title=title, message=message)
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def get_user_notifications(cls, user_id, unread_only=False):
        """Получить уведомления пользователя"""
        query = cls.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(cls.created_at.desc()).all()

    def mark_as_read(self):
        """Отметить уведомление как прочитанное"""
        self.is_read = True
        db.session.commit()

# Для SQLite триггеры нужно создавать с помощью DDL после создания таблиц
# Этот код будет выполнен при инициализации базы данных
def create_triggers():
    trigger_sql = """
    DROP TRIGGER IF EXISTS assessment_insert_trigger;
    DROP TRIGGER IF EXISTS assessment_update_trigger;

    CREATE TRIGGER assessment_insert_trigger
    AFTER INSERT ON assessments
    FOR EACH ROW
    BEGIN
        UPDATE enrollments
        SET progress = (
            SELECT (COUNT(DISTINCT a.module_id) * 100.0 / NULLIF(COUNT(DISTINCT m.id), 0))
            FROM assessments a
            JOIN modules m ON m.course_id = (
                SELECT course_id FROM modules WHERE id = NEW.module_id
            )
            WHERE a.user_id = NEW.user_id AND a.grade > 0
        ),
        last_accessed = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id
        AND course_id = (SELECT course_id FROM modules WHERE id = NEW.module_id);
    END;

    CREATE TRIGGER assessment_update_trigger
    AFTER UPDATE ON assessments
    FOR EACH ROW
    BEGIN
        UPDATE enrollments
        SET progress = (
            SELECT (COUNT(DISTINCT a.module_id) * 100.0 / NULLIF(COUNT(DISTINCT m.id), 0))
            FROM assessments a
            JOIN modules m ON m.course_id = (
                SELECT course_id FROM modules WHERE id = NEW.module_id
            )
            WHERE a.user_id = NEW.user_id AND a.grade > 0
        ),
        last_accessed = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id
        AND course_id = (SELECT course_id FROM modules WHERE id = NEW.module_id);
    END;
    """
    db.session.execute(trigger_sql)
    db.session.commit()

