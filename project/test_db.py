#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для тестирования базы данных и добавления тестового пользователя.
Запускать после успешной инициализации базы данных.
Использование: python test_db.py
"""

import os
import sqlite3
import sys
import hashlib

def test_db():
    """Тестирует базу данных и добавляет тестового пользователя."""
    print("Тестирование базы данных и добавление тестового пользователя...")

    try:
        # Определяем пути к файлам
        current_dir = os.path.dirname(os.path.abspath(__file__))
        instance_dir = os.path.join(current_dir, 'instance')
        db_path = os.path.join(instance_dir, 'db.sqlite3')

        # Проверяем, существует ли база данных
        if not os.path.exists(db_path):
            print(f"Ошибка: База данных не найдена: {db_path}")
            print("Сначала запустите 'python no_flask_init_db.py' для создания базы данных.")
            return False

        # Подключаемся к базе данных
        print(f"Подключение к базе данных: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получаем список таблиц для проверки структуры
        print("Проверка структуры базы данных...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        print(f"Найдены таблицы: {table_names}")

        # Проверяем наличие необходимых таблиц
        required_tables = ['users', 'courses', 'modules', 'enrollments', 'assessments', 'feedbacks', 'attachments', 'notifications']
        missing_tables = [table for table in required_tables if table not in table_names]

        if missing_tables:
            print(f"Ошибка: Отсутствуют следующие таблицы: {missing_tables}")
            return False

        # Генерируем простой хеш пароля (для демо)
        password = "admin123"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Проверяем, существует ли пользователь admin@example.com
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@example.com",))
        existing_user = cursor.fetchone()

        if existing_user:
            print("Тестовый пользователь admin@example.com уже существует. Пропускаем создание.")
        else:
            # Добавляем тестового пользователя
            print("Добавление тестового пользователя...")
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("Admin User", "admin@example.com", hashed_password, "admin")
            )
            conn.commit()
            print("Тестовый пользователь успешно добавлен:")
            print("  - Email: admin@example.com")
            print("  - Пароль: admin123")
            print("  - Роль: admin")

        # Добавляем тестовый курс, если его еще нет
        cursor.execute("SELECT id FROM courses WHERE title = ?", ("Тестовый курс",))
        existing_course = cursor.fetchone()

        if existing_course:
            print("Тестовый курс уже существует. Пропускаем создание.")
        else:
            print("Добавление тестового курса...")
            cursor.execute(
                "INSERT INTO courses (title, description) VALUES (?, ?)",
                ("Тестовый курс", "Описание тестового курса для проверки функциональности.")
            )
            course_id = cursor.lastrowid

            # Добавляем модуль к курсу
            cursor.execute(
                "INSERT INTO modules (course_id, title, content) VALUES (?, ?, ?)",
                (course_id, "Введение в курс", "Содержание вводного модуля курса.")
            )

            conn.commit()
            print("Тестовый курс и модуль успешно добавлены.")

        # Закрываем соединение
        conn.close()

        print("База данных успешно протестирована.")
        print("Теперь вы можете запустить приложение: python run.py")

        return True
    except Exception as e:
        print(f"Ошибка при тестировании базы данных: {e}")
        return False

if __name__ == '__main__':
    success = test_db()
    sys.exit(0 if success else 1)
