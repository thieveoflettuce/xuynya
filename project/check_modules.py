#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для проверки доступности модулей.
Используйте: python check_modules.py
"""

import sys
import os

def check_modules():
    print("Проверка доступности модулей...")
    print(f"Python версия: {sys.version}")
    print(f"Python путь: {sys.executable}")
    print(f"Рабочая директория: {os.getcwd()}")
    
    modules = [
        "flask",
        "flask_sqlalchemy",
        "sqlalchemy",
        "flask_bcrypt",
        "flask_jwt_extended",
        "flask_migrate",
        "flask_cors"
    ]
    
    success = True
    
    for module_name in modules:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "Версия не указана")
            print(f"✓ {module_name} - импортирован успешно (версия: {version})")
        except ImportError as e:
            print(f"✗ {module_name} - ОШИБКА: {e}")
            success = False
    
    # Проверяем путь к системным модулям
    print("\nПути импорта Python:")
    for path in sys.path:
        print(f"  - {path}")
    
    # Проверяем путь к модулям проекта
    if os.path.exists('app'):
        print("\nСтруктура директории app:")
        for root, dirs, files in os.walk('app'):
            for file in files:
                if file.endswith('.py'):
                    print(f"  - {os.path.join(root, file)}")
    
    # Тестируем импорт из проекта
    try:
        from app import create_app
        print("✓ app.create_app - импортирован успешно")
    except ImportError as e:
        print(f"✗ app.create_app - ОШИБКА: {e}")
        success = False
    
    if success:
        print("\nВсе модули доступны и импортируются успешно!")
        print("Проблема может быть в другом месте.")
    else:
        print("\nНе все модули доступны. Проверьте установку пакетов и виртуальное окружение.")
    
    return success

if __name__ == '__main__':
    check_modules()