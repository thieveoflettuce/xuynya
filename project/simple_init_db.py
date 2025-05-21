#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Максимально простой скрипт для создания базы данных без триггеров.
Используйте: python simple_init_db.py
"""

import os
import sqlite3
import sys

def create_db():
    """Создает и инициализирует базу данных SQLite без триггеров."""
    print("Сверхпростая инициализация базы данных SQLite...")
    
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
        
        # Выполняем скрипт schema.sql, если файл существует
        if os.path.exists(schema_path):
            print("Применение схемы из файла schema.sql...")
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()
            
            # Выполняем SQL-запросы
            conn.executescript(schema_script)
            conn.commit()
            print("Схема базы данных успешно применена.")
        else:
            print(f"ОШИБКА: Файл схемы не найден: {schema_path}")
            return False
        
        # Добавляем тестового пользователя
        print("Добавление тестового пользователя...")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("Admin", "admin@example.com", "pbkdf2:sha256:150000$GJH8TzqP$63336289d5d5afa68f0d3144862c29e340956e927fa897a7b2b876e9fdce89d4", "admin")
        )
        conn.commit()
        print("Тестовый пользователь добавлен.")
        
        # Закрываем соединение
        conn.close()
        
        print("База данных успешно инициализирована без триггеров!")
        print("ВНИМАНИЕ: Триггеры не были добавлены. Некоторая функциональность может быть ограничена.")
        
        return True
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        return False

if __name__ == '__main__':
    success = create_db()
    sys.exit(0 if success else 1)