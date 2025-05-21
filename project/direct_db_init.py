#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для прямой инициализации базы данных SQLite без Flask-SQLAlchemy.
Этот скрипт создает всю необходимую структуру базы данных напрямую через SQLite.
"""

import os
import sqlite3
import sys
import hashlib

def init_db():
    """Создаёт базу данных и все необходимые таблицы."""
    try:
        # Определяем пути
        current_dir = os.path.dirname(os.path.abspath(__file__))
        instance_dir = os.path.join(current_dir, 'instance')
        db_path = os.path.join(instance_dir, 'db.sqlite3')
        
        # Создаем директорию instance, если ее нет
        os.makedirs(instance_dir, exist_ok=True)
        
        # Удаляем существующую базу данных, если она есть
        if os.path.exists(db_path):
            print(f"Удаление существующей базы данных: {db_path}")
            os.remove(db_path)
        
        print(f"Создание новой базы данных: {db_path}")
        
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Создаем таблицы
        print("Создание таблиц...")
        
        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # Индекс для ускорения поиска по email
        cursor.execute('''
        CREATE INDEX idx_users_email ON users(email);
        ''')
        
        # Таблица курсов
        cursor.execute('''
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # Таблица модулей (разделов) курса
        cursor.execute('''
        CREATE TABLE modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        ''')
        
        # Таблица регистрации пользователя на курсы
        cursor.execute('''
        CREATE TABLE enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            progress FLOAT DEFAULT 0.0,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        ''')
        
        # Уникальный индекс для предотвращения двойной регистрации
        cursor.execute('''
        CREATE UNIQUE INDEX idx_enrollments_user_course ON enrollments(user_id, course_id);
        ''')
        
        # Таблица оценок за модули
        cursor.execute('''
        CREATE TABLE assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            grade FLOAT NOT NULL DEFAULT 0.0,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')
        
        # Таблица отзывов о курсах
        cursor.execute('''
        CREATE TABLE feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment TEXT,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')
        
        # Уникальный индекс для предотвращения множественных отзывов от одного пользователя
        cursor.execute('''
        CREATE UNIQUE INDEX idx_feedbacks_user_course ON feedbacks(user_id, course_id);
        ''')
        
        # Таблица вложений (файлов) к модулям
        cursor.execute('''
        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_size INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
        ''')
        
        # Индекс для ускорения поиска вложений по модулю
        cursor.execute('''
        CREATE INDEX idx_attachments_module ON attachments(module_id);
        ''')
        
        # Таблица уведомлений
        cursor.execute('''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')
        
        # Индекс для ускорения поиска непрочитанных уведомлений пользователя
        cursor.execute('''
        CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
        ''')
        
        # Создание триггеров
        print("Создание триггеров...")
        
        # Триггер для обновления прогресса при добавлении оценки
        cursor.execute('''
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
        ''')
        
        # Триггер для обновления прогресса при обновлении оценки
        cursor.execute('''
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
        ''')
        
        # Триггер для создания уведомлений при добавлении новых модулей в курс
        cursor.execute('''
        CREATE TRIGGER module_add_notification_trigger
        AFTER INSERT ON modules
        FOR EACH ROW
        BEGIN
            INSERT INTO notifications (user_id, title, message, is_read, created_at)
            SELECT
                e.user_id,
                'Новый модуль в курсе',
                'В курс ' || (SELECT title FROM courses WHERE id = NEW.course_id) || ' добавлен новый модуль: ' || NEW.title,
                0,
                CURRENT_TIMESTAMP
            FROM
                enrollments e
            WHERE
                e.course_id = NEW.course_id;
        END;
        ''')
        
        # Добавляем тестового пользователя (admin)
        print("Добавление тестового пользователя (admin@example.com / admin123)...")
        
        # Простой хеш пароля
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        ''', ("Admin User", "admin@example.com", password_hash, "admin"))
        
        # Добавляем тестовый курс
        print("Добавление тестового курса...")
        
        cursor.execute('''
        INSERT INTO courses (title, description)
        VALUES (?, ?)
        ''', ("Тестовый курс", "Описание тестового курса для проверки функциональности."))
        
        course_id = cursor.lastrowid
        
        # Добавляем тестовый модуль
        cursor.execute('''
        INSERT INTO modules (course_id, title, content)
        VALUES (?, ?, ?)
        ''', (course_id, "Введение в курс", "Содержание вводного модуля курса."))
        
        # Сохраняем изменения и закрываем соединение
        conn.commit()
        conn.close()
        
        print("База данных успешно инициализирована!")
        print("Теперь вы можете запустить приложение: python run.py")
        
        return True
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        return False

if __name__ == "__main__":
    init_db()