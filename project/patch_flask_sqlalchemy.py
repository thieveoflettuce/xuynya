#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для патча flask_sqlalchemy для обхода проблемы с __all__ в SQLAlchemy.
"""

import os
import sys
import importlib.util

def find_flask_sqlalchemy_path():
    """Находит путь к flask_sqlalchemy."""
    spec = importlib.util.find_spec('flask_sqlalchemy')
    if spec is None:
        print("Ошибка: flask_sqlalchemy не найден!")
        return None
    
    init_path = os.path.join(spec.submodule_search_locations[0], '__init__.py')
    if not os.path.exists(init_path):
        print(f"Ошибка: {init_path} не найден!")
        return None
    
    return init_path

def patch_flask_sqlalchemy():
    """Патчит flask_sqlalchemy для решения проблемы с __all__."""
    init_path = find_flask_sqlalchemy_path()
    if init_path is None:
        return False
    
    print(f"Найден файл flask_sqlalchemy/__init__.py: {init_path}")
    
    # Создаем резервную копию
    backup_path = init_path + '.bak'
    if not os.path.exists(backup_path):
        print("Создание резервной копии...")
        with open(init_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"Резервная копия создана: {backup_path}")
    
    # Читаем файл
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Патчим проблемное место
    if "for key in module.__all__:" in content:
        print("Патчим код, связанный с module.__all__...")
        
        # Заменяем проблемное место
        patched_content = content.replace(
            "for key in module.__all__:",
            "# Патч для обхода проблемы с отсутствием module.__all__\n"
            "    all_symbols = getattr(module, '__all__', dir(module))\n"
            "    for key in all_symbols:"
        )
        
        # Записываем обновленный файл
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print("flask_sqlalchemy успешно пропатчен!")
        
        # Перезагружаем модуль
        print("Перезагрузка flask_sqlalchemy...")
        if 'flask_sqlalchemy' in sys.modules:
            del sys.modules['flask_sqlalchemy']
        
        return True
    else:
        print("Патч не требуется или формат файла не соответствует ожидаемому.")
        return False

if __name__ == "__main__":
    result = patch_flask_sqlalchemy()
    if result:
        print("Патч успешно применен. Попробуйте запустить приложение снова.")
    else:
        print("Не удалось применить патч.")