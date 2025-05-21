-- Хранимая процедура для обновления прогресса пользователя по курсу
CREATE OR REPLACE PROCEDURE update_user_progress(
    user_id_param INTEGER,
    course_id_param INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    new_progress FLOAT;
BEGIN
    -- Проверка наличия регистрации пользователя на курсе
    IF NOT EXISTS (
        SELECT 1 FROM enrollments
        WHERE user_id = user_id_param AND course_id = course_id_param
    ) THEN
        RAISE EXCEPTION 'Пользователь не зарегистрирован на этот курс';
    END IF;

    -- Вычисление нового прогресса с использованием нашей функции
    new_progress := calculate_user_progress(user_id_param, course_id_param);

    -- Обновление записи о прогрессе
    UPDATE enrollments
    SET
        progress = new_progress,
        last_accessed = CURRENT_TIMESTAMP
    WHERE
        user_id = user_id_param
        AND course_id = course_id_param;
END;
$$;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых процедур через SQL напрямую,
-- мы будем использовать эту процедуру через Python.
-- Процедура будет реализована в Python-коде как:
--
-- def update_user_progress(user_id, course_id):
--     # Проверка наличия регистрации пользователя на курсе
--     enrollment = Enrollment.query.filter_by(
--         user_id=user_id, course_id=course_id).first()
--
--     if not enrollment:
--         raise ValueError("Пользователь не зарегистрирован на этот курс")
--
--     # Вычисление нового прогресса с использованием нашей функции
--     new_progress = calculate_user_progress(user_id, course_id)
--
--     # Обновление записи о прогрессе
--     enrollment.progress = new_progress
--     enrollment.last_accessed = datetime.now()
--     db.session.commit()
--
--     return enrollment
