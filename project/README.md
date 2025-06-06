# Инструкция по инициализации базы данных

В этом проекте есть несколько способов инициализировать базу данных. Выберите любой из них, который работает в вашей среде.

## Способ 1: Использование прямого скрипта SQLite (рекомендуется)

Этот способ не требует настройки Flask CLI и использует напрямую SQLite:

```bash
cd project
python create_db_direct.py
```

## Способ 2: Через скрипт инициализации Flask

```bash
cd project
python init_db.py
```

## Способ 3: Через Flask CLI (если настроен)

```bash
cd project
flask init-db
```

или

```bash
cd project
python -m flask init-db
```

## Способ 4: Через полный путь к Flask

Если Flask установлен в виртуальном окружении:

```bash
# Windows
venv\Scripts\flask.exe init-db

# Linux/Mac
venv/bin/flask init-db
```

## Решение проблем

### Ошибка: "file is not a database"

Эта ошибка означает, что файл базы данных поврежден. Используйте скрипт `create_db_direct.py` или `init_db.py`, который автоматически удалит старую базу данных и создаст новую.

### Ошибка: "flask не является внутренней или внешней командой"

Это означает, что Flask не установлен или не доступен в переменных среды. Используйте альтернативные способы (1 или 2).

### Ошибка: "module 'sqlalchemy' has no attribute '__all__'"

Эта ошибка связана с несовместимостью версий SQLAlchemy. Убедитесь, что вы используете правильные версии:

```bash
pip install flask-sqlalchemy==3.0.3 sqlalchemy==2.0.23
```

## Запуск приложения после инициализации

После успешной инициализации базы данных запустите приложение:

```bash
cd project
python run.py
```
