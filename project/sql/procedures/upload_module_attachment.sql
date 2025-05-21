-- Хранимая процедура для загрузки вложения к модулю
CREATE OR REPLACE PROCEDURE upload_module_attachment(
    module_id_param INTEGER,
    filename_param TEXT,
    file_path_param TEXT,
    file_type_param TEXT,
    file_size_param INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Проверка существования модуля
    IF NOT EXISTS (SELECT 1 FROM modules WHERE id = module_id_param) THEN
        RAISE EXCEPTION 'Модуль с ID % не найден', module_id_param;
    END IF;

    -- Добавление вложения
    INSERT INTO attachments (module_id, filename, file_path, file_type, file_size, uploaded_at)
    VALUES (module_id_param, filename_param, file_path_param, file_type_param, file_size_param, CURRENT_TIMESTAMP);

    -- Создание уведомлений для всех пользователей, зарегистрированных на курс
    INSERT INTO notifications (user_id, title, message, is_read, created_at)
    SELECT
        e.user_id,
        'Новое вложение в модуле',
        'В модуль ' || (SELECT title FROM modules WHERE id = module_id_param) ||
        ' курса ' || (SELECT c.title FROM courses c JOIN modules m ON c.id = m.course_id WHERE m.id = module_id_param) ||
        ' добавлено новое вложение: ' || filename_param,
        FALSE,
        CURRENT_TIMESTAMP
    FROM
        modules m
    JOIN
        enrollments e ON m.course_id = e.course_id
    WHERE
        m.id = module_id_param;
END;
$$;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых процедур через SQL напрямую,
-- мы будем использовать эту процедуру через Python.
-- Процедура будет реализована в Python-коде как:
--
-- def upload_module_attachment(module_id, filename, file_path, file_type, file_size):
--     # Проверка существования модуля
--     module = Module.query.get(module_id)
--     if not module:
--         raise ValueError(f"Модуль с ID {module_id} не найден")
--
--     # Добавление вложения
--     attachment = Attachment(
--         module_id=module_id,
--         filename=filename,
--         file_path=file_path,
--         file_type=file_type,
--         file_size=file_size
--     )
--     db.session.add(attachment)
--
--     # Создание уведомлений для всех пользователей, зарегистрированных на курс
--     enrollments = Enrollment.query.filter_by(course_id=module.course_id).all()
--     for enrollment in enrollments:
--         notification = Notification(
--             user_id=enrollment.user_id,
--             title='Новое вложение в модуле',
--             message=f'В модуль {module.title} курса {module.course.title} добавлено новое вложение: {filename}',
--             is_read=False
--         )
--         db.session.add(notification)
--
--     db.session.commit()
--     return attachment
