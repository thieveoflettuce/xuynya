-- Хранимая процедура для создания уведомления для пользователя
CREATE OR REPLACE PROCEDURE create_user_notification(
    user_id_param INTEGER,
    title_param TEXT,
    message_param TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Проверка существования пользователя
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = user_id_param) THEN
        RAISE EXCEPTION 'Пользователь с ID % не найден', user_id_param;
    END IF;

    -- Создание уведомления
    INSERT INTO notifications (user_id, title, message, is_read, created_at)
    VALUES (user_id_param, title_param, message_param, FALSE, CURRENT_TIMESTAMP);
END;
$$;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых процедур через SQL напрямую,
-- мы будем использовать эту процедуру через Python.
-- Процедура будет реализована в Python-коде как:
--
-- def create_user_notification(user_id, title, message):
--     # Проверка существования пользователя
--     user = User.query.get(user_id)
--     if not user:
--         raise ValueError(f"Пользователь с ID {user_id} не найден")
--
--     # Создание уведомления
--     notification = Notification(
--         user_id=user_id,
--         title=title,
--         message=message,
--         is_read=False
--     )
--     db.session.add(notification)
--     db.session.commit()
--
--     return notification
