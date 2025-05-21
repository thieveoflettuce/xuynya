-- Триггер для автоматического обновления прогресса пользователя при добавлении/изменении оценки
CREATE OR REPLACE FUNCTION update_enrollment_progress_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    course_id_val INTEGER;
BEGIN
    -- Получаем ID курса, к которому принадлежит модуль
    SELECT course_id INTO course_id_val
    FROM modules
    WHERE id = NEW.module_id;

    -- Вызываем хранимую процедуру для обновления прогресса
    IF course_id_val IS NOT NULL THEN
        CALL update_user_progress(NEW.user_id, course_id_val);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера, который срабатывает после добавления или обновления записи в таблице assessments
CREATE TRIGGER assessment_update_trigger
AFTER INSERT OR UPDATE ON assessments
FOR EACH ROW
EXECUTE FUNCTION update_enrollment_progress_trigger_function();

-- Для SQLite:
-- Поскольку SQLite имеет ограниченную поддержку триггеров и не поддерживает хранимые процедуры,
-- мы можем создать более простую версию триггера:
--
-- CREATE TRIGGER assessment_update_trigger
-- AFTER INSERT ON assessments
-- BEGIN
--     UPDATE enrollments
--     SET progress = (
--         SELECT (COUNT(DISTINCT a.module_id) * 100.0 / COUNT(DISTINCT m.id))
--         FROM assessments a
--         JOIN modules m ON m.course_id = (
--             SELECT course_id FROM modules WHERE id = NEW.module_id
--         )
--         WHERE a.user_id = NEW.user_id AND a.grade > 0
--     ),
--     last_accessed = CURRENT_TIMESTAMP
--     WHERE user_id = NEW.user_id
--     AND course_id = (SELECT course_id FROM modules WHERE id = NEW.module_id);
-- END;
