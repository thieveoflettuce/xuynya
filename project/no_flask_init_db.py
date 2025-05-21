#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Полностью независимый скрипт для создания базы данных без Flask или SQLAlchemy.
Используйте: python no_flask_init_db.py
"""

import os
import sqlite3
import sys

def create_db():
    """Создает и инициализирует базу данных SQLite без зависимостей от Flask."""
    print("Независимая инициализация базы данных SQLite...")

    try:
        # Определяем пути к файлам
        current_dir = os.path.dirname(os.path.abspath(__file__))
        instance_dir = os.path.join(current_dir, 'instance')
        db_path = os.path.join(instance_dir, 'db.sqlite3')
        schema_path = os.path.join(current_dir, 'sql', 'schema.sql')

        # Создаем директорию instance, если ее нет
        os.makedirs(instance_dir, exist_ok=True)

        # Удаляем существующую базу данных, если она есть
        if os.path.exists(db_path):
            print(f"Удаление существующей базы данных: {db_path}")
            os.remove(db_path)
            print("Существующая база данных удалена.")

        # Создаем новую базу данных
        print(f"Создание новой базы данных: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверяем, существует ли файл schema.sql
        if not os.path.exists(schema_path):
            print(f"Файл схемы не найден: {schema_path}")
            print("Создаем базовую схему...")

            # Создаем базовую схему, если файл schema.sql не найден
            basic_schema = """
            -- Создание таблиц для базы данных

            -- Таблица пользователей
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(128) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Индекс для ускорения поиска по email
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

            -- Таблица курсов
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Таблица модулей (разделов) курса
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

            -- Таблица регистрации пользователя на курсы
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                progress FLOAT DEFAULT 0.0,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

            -- Уникальный индекс для предотвращения двойной регистрации
            CREATE UNIQUE INDEX IF NOT EXISTS idx_enrollments_user_course ON enrollments(user_id, course_id);

            -- Таблица оценок за модули
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                grade FLOAT NOT NULL DEFAULT 0.0,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            -- Таблица отзывов о курсах
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment TEXT,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            -- Уникальный индекс для предотвращения множественных отзывов от одного пользователя
            CREATE UNIQUE INDEX IF NOT EXISTS idx_feedbacks_user_course ON feedbacks(user_id, course_id);

            -- Таблица вложений (файлов) к модулям
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                file_type VARCHAR(50),
                file_size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
            );

            -- Индекс для ускорения поиска вложений по модулю
            CREATE INDEX IF NOT EXISTS idx_attachments_module ON attachments(module_id);

            -- Таблица уведомлений
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            -- Индекс для ускорения поиска непрочитанных уведомлений пользователя
            CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);
            """

            conn.executescript(basic_schema)
            conn.commit()
        else:
            # Выполняем скрипт schema.sql, если файл существует
            print("Применение схемы из файла schema.sql...")
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()

            # Выполняем SQL-запросы
            conn.executescript(schema_script)
            conn.commit()

        print("Схема базы данных успешно применена.")

        # Создаем триггеры
        print("Создание триггеров...")
        triggers_sql = """
        -- Триггер для обновления прогресса при добавлении или обновлении оценки
        CREATE TRIGGER IF NOT EXISTS assessment_update_trigger
        AFTER INSERT OR UPDATE ON assessments
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

        -- Триггер для создания уведомлений при добавлении новых модулей в курс
        CREATE TRIGGER IF NOT EXISTS module_add_notification_trigger
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
        """

        # Выполняем SQL-запросы для триггеров
        conn.executescript(triggers_sql)
        conn.commit()

        # Закрываем соединение
        conn.close()

        print("Триггеры успешно созданы.")
        print("База данных успешно инициализирована!")

        return True
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        return False

if __name__ == '__main__':
    success = create_db()
    sys.exit(0 if success else 1)
