-- Функция для подсчета количества непрочитанных уведомлений пользователя
CREATE OR REPLACE FUNCTION get_user_notifications_count(user_id_param INTEGER)
RETURNS INTEGER AS $$
DECLARE
    unread_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO unread_count
    FROM notifications
    WHERE user_id = user_id_param AND is_read = FALSE;

    RETURN COALESCE(unread_count, 0);
END;
$$ LANGUAGE plpgsql;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых функций через SQL напрямую,
-- мы будем использовать эту функцию через Python.
-- Функция будет реализована в Python-коде как:
--
-- def get_user_notifications_count(user_id):
--     query = "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0"
--     result = db.session.execute(query, (user_id,)).scalar()
--     return result or 0
