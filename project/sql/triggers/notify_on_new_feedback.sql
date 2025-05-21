-- Триггер для автоматического создания уведомления при добавлении нового отзыва
CREATE OR REPLACE FUNCTION notify_on_new_feedback_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    reviewer_name TEXT;
BEGIN
    -- Получаем название курса
    SELECT title INTO course_title
    FROM courses
    WHERE id = NEW.course_id;

    -- Получаем имя пользователя, оставившего отзыв
    SELECT name INTO reviewer_name
    FROM users
    WHERE id = NEW.user_id;

    -- Создаем уведомление для автора курса
    INSERT INTO notifications (
        user_id,
        title,
        message,
        is_read,
        created_at
    )
    SELECT
        u.id,
        'Новый отзыв о курсе',
        'Пользователь ' || reviewer_name || ' оставил отзыв о курсе "' || course_title ||
        '" с оценкой ' || NEW.rating || ' из 5',
        FALSE,
        CURRENT_TIMESTAMP
    FROM
        users u
    WHERE
        u.role = 'teacher';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера, который срабатывает после добавления записи в таблице feedbacks
CREATE TRIGGER feedback_notification_trigger
AFTER INSERT ON feedbacks
FOR EACH ROW
EXECUTE FUNCTION notify_on_new_feedback_trigger_function();

-- Для SQLite:
-- Поскольку SQLite имеет ограниченную поддержку триггеров,
-- мы можем создать более простую версию триггера:
--
-- CREATE TRIGGER feedback_notification_trigger
-- AFTER INSERT ON feedbacks
-- BEGIN
--     INSERT INTO notifications (user_id, title, message, is_read, created_at)
--     SELECT
--         u.id,
--         'Новый отзыв о курсе',
--         'Пользователь ' || (SELECT name FROM users WHERE id = NEW.user_id) ||
--         ' оставил отзыв о курсе "' || (SELECT title FROM courses WHERE id = NEW.course_id) ||
--         '" с оценкой ' || NEW.rating || ' из 5',
--         0,
--         CURRENT_TIMESTAMP
--     FROM
--         users u
--     WHERE
--         u.role = 'teacher';
-- END;
