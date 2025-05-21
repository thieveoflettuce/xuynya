#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для инициализации базы данных.
Используйте: python init_db.py
"""

import os
import sys
from app import create_app, db
from app.models import create_triggers

def init_db():
    """Инициализирует базу данных и создает все таблицы и триггеры."""
    print("Инициализация базы данных...")

    # Создаем приложение и контекст
    app = create_app()

    with app.app_context():
        try:
            # Убедимся, что директория instance существует
            instance_path = os.path.join(app.root_path, '..', 'instance')
            os.makedirs(instance_path, exist_ok=True)

            # Удалим существующую базу данных, если она есть
            db_path = os.path.join(instance_path, 'db.sqlite3')
            if os.path.exists(db_path):
                print(f"Удаление существующей базы данных: {db_path}")
                os.remove(db_path)
                print("Существующая база данных удалена.")

            # Создание новых таблиц
            print("Создание новых таблиц...")
            db.create_all()

            # Создание триггеров
            print("Создание триггеров...")
            create_triggers()

            print("База данных успешно инициализирована!")
            return True
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            return False

if __name__ == '__main__':
    success = init_db()
    sys.exit(0 if success else 1)
