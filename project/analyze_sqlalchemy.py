#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для анализа содержимого flask_sqlalchemy/__init__.py
"""

import os
import importlib.util

def analyze_flask_sqlalchemy():
    """Анализирует содержимое flask_sqlalchemy/__init__.py."""
    spec = importlib.util.find_spec('flask_sqlalchemy')
    if spec is None:
        print("Ошибка: flask_sqlalchemy не найден!")
        return False
    
    init_path = os.path.join(spec.submodule_search_locations[0], '__init__.py')
    if not os.path.exists(init_path):
        print(f"Ошибка: {init_path} не найден!")
        return False
    
    print(f"Найден файл flask_sqlalchemy/__init__.py: {init_path}")
    
    # Читаем файл и ищем проблемное место
    with open(init_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Всего строк: {len(lines)}")
    
    # Ищем ключевые части кода
    include_sqlalchemy_line = None
    all_line = None
    
    for i, line in enumerate(lines):
        if "_include_sqlalchemy" in line:
            print(f"Строка [{i+1}]: {line.strip()}")
            include_sqlalchemy_line = i
        
        if "module.__all__" in line:
            print(f"Строка [{i+1}]: {line.strip()}")
            all_line = i
    
    if include_sqlalchemy_line is not None:
        print("\nФункция _include_sqlalchemy:")
        start = include_sqlalchemy_line
        end = min(start + 30, len(lines))
        for i in range(start, end):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
    
    # Возвращаем информацию о версии
    try:
        import flask_sqlalchemy
        print(f"\nВерсия flask_sqlalchemy: {flask_sqlalchemy.__version__}")
    except (ImportError, AttributeError):
        print("\nНе удалось определить версию flask_sqlalchemy")
    
    try:
        import sqlalchemy
        print(f"Версия sqlalchemy: {sqlalchemy.__version__}")
    except (ImportError, AttributeError):
        print("Не удалось определить версию sqlalchemy")

if __name__ == "__main__":
    analyze_flask_sqlalchemy()