# Инструкции по запуску проекта

## Требования

### Для бэкенда (Flask)
- Python 3.8 или выше
- Flask и другие зависимости указаны в файле `requirements.txt`

### Для фронтенда (React)
- Node.js 14 или выше
- npm или bun

## Установка

### Бэкенд

1. Создайте виртуальное окружение Python:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
   - Для Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Для Linux/macOS:
   ```bash
   source venv/bin/activate
   ```

3. Перейдите в директорию проекта:
```bash
cd project
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Инициализируйте базу данных:
```bash
flask init-db
```

### Фронтенд

1. Перейдите в директорию фронтенда:
```bash
cd project/frontend
```

2. Установите зависимости:
```bash
npm install
# или
bun install
```

## Запуск

### Бэкенд

1. Находясь в директории проекта, запустите сервер Flask:
```bash
python run.py
```

Сервер будет запущен по адресу: http://localhost:5000

### Фронтенд

1. Находясь в директории frontend, запустите сервер разработки:
```bash
npm run dev
# или
bun run dev
```

Фронтенд будет доступен по адресу: http://localhost:3000

## Тестовые пользователи

В системе уже созданы тестовые учетные записи:

1. **Администратор**:
   - Email: admin@example.com
   - Пароль: admin123

2. **Преподаватель**:
   - Email: teacher@example.com
   - Пароль: teacher123

3. **Студент**:
   - Email: student@example.com
   - Пароль: student123

## Дополнительная информация

### Структура проекта

- `project/app/` - бэкенд на Flask
  - `__init__.py` - инициализация приложения
  - `auth.py` - контроллер для авторизации
  - `courses.py` - основной API для работы с курсами
  - `models.py` - модели данных
  - `attachments.py` - API для работы с вложениями
  - `notifications.py` - API для работы с уведомлениями

- `project/sql/` - SQL скрипты
  - `schema.sql` - схема базы данных
  - `functions/` - пользовательские функции
  - `procedures/` - хранимые процедуры
  - `triggers/` - триггеры
  - `queries/` - сложные запросы

- `project/frontend/` - фронтенд на React
  - `src/` - исходный код
    - `components/` - компоненты
    - `contexts/` - контексты React
    - `pages/` - страницы
    - `services/` - сервисы для работы с API

### API

Основные эндпоинты API:

- **Авторизация**
  - `POST /auth/register` - регистрация нового пользователя
  - `POST /auth/login` - вход в систему
  - `GET /auth/profile` - получение профиля

- **Курсы**
  - `GET /api/courses` - список всех курсов
  - `GET /api/courses/<id>` - информация о конкретном курсе
  - `POST /api/courses` - создание нового курса
  - `PUT /api/courses/<id>` - обновление курса
  - `DELETE /api/courses/<id>` - удаление курса

- **Модули**
  - `GET /api/courses/<course_id>/modules` - модули курса
  - `POST /api/courses/<course_id>/modules` - создание модуля
  - `PUT /api/modules/<id>` - обновление модуля
  - `DELETE /api/modules/<id>` - удаление модуля

- **Регистрация на курсы**
  - `POST /api/courses/<course_id>/enroll` - запись на курс
  - `GET /api/enrollments` - курсы пользователя
  - `DELETE /api/courses/<course_id>/unenroll` - отмена записи

- **Отзывы**
  - `GET /api/courses/<course_id>/feedbacks` - отзывы о курсе
  - `POST /api/courses/<course_id>/feedback` - создание отзыва
  - `DELETE /api/feedbacks/<id>` - удаление отзыва

- **Уведомления**
  - `GET /api/notifications` - уведомления пользователя
  - `GET /api/notifications/count` - количество непрочитанных
  - `PUT /api/notifications/<id>/read` - отметить как прочитанное
  - `PUT /api/notifications/read-all` - отметить все как прочитанные
  - `DELETE /api/notifications/<id>` - удаление уведомления

- **Вложения**
  - `GET /api/modules/<module_id>/attachments` - вложения модуля
  - `POST /api/modules/<module_id>/attachments` - загрузка вложения
  - `DELETE /api/attachments/<id>` - удаление вложения

### Требования безопасности

При развертывании проекта в продакшн не забудьте:

1. Изменить секретные ключи в конфигурации
2. Настроить HTTPS
3. Настроить CORS правильно
4. Ограничить доступ к API с помощью rate limiting
