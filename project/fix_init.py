#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def fix_init_file():
    """Исправляет файл __init__.py для работы с SQLAlchemy."""
    init_file_path = os.path.join('app', '__init__.py')
    
    if not os.path.exists(init_file_path):
        print(f"Ошибка: Файл {init_file_path} не найден!")
        return False
    
    print(f"Исправление файла {init_file_path}...")
    
    # Читаем файл
    with open(init_file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # Создаем резервную копию
    with open(init_file_path + '.bak', 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    # Ищем и заменяем строку инициализации SQLAlchemy
    for i, line in enumerate(content):
        if "db = SQLAlchemy(" in line:
            content[i] = "db = SQLAlchemy()\n"
            print("Заменена строка инициализации SQLAlchemy")
    
    # Записываем обновленное содержимое
    with open(init_file_path, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print(f"Файл {init_file_path} успешно исправлен!")
    return True

if __name__ == '__main__':
    fix_init_file()