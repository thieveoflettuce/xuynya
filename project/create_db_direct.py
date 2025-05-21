#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Простой скрипт для инициализации базы данных SQLite напрямую,
без использования Flask или SQLAlchemy.
Используйте: python create_db_direct.py
"""

import os
import sqlite3
import sys

def create_db():
    """Создает базу данных SQLite и инициализирует таблицы из schema.sql."""
    print("Прямая инициализация базы данных SQLite...")

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

        # Выполняем скрипт schema.sql
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
