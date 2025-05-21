-- Хранимая процедура для регистрации пользователя на курсе
CREATE OR REPLACE PROCEDURE enroll_user_in_course(
    user_id_param INTEGER,
    course_id_param INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    existing_enrollment INTEGER;
BEGIN
    -- Проверка существования пользователя
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = user_id_param) THEN
        RAISE EXCEPTION 'Пользователь с ID % не найден', user_id_param;
    END IF;

    -- Проверка существования курса
    IF NOT EXISTS (SELECT 1 FROM courses WHERE id = course_id_param) THEN
        RAISE EXCEPTION 'Курс с ID % не найден', course_id_param;
    END IF;

    -- Проверка, не зарегистрирован ли пользователь уже на этот курс
    SELECT id INTO existing_enrollment
    FROM enrollments
    WHERE user_id = user_id_param AND course_id = course_id_param;

    IF existing_enrollment IS NOT NULL THEN
        RAISE EXCEPTION 'Пользователь уже зарегистрирован на этот курс';
    END IF;

    -- Регистрация пользователя на курсе
    INSERT INTO enrollments (user_id, course_id, progress)
    VALUES (user_id_param, course_id_param, 0.0);

    -- Дополнительная логика при необходимости
    -- Например, автоматическое добавление записей для оценки модулей
END;
$$;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых процедур через SQL напрямую,
-- мы будем использовать эту процедуру через Python.
-- Процедура будет реализована в Python-коде как:
--
-- def enroll_user_in_course(user_id, course_id):
--     # Проверка существования пользователя
--     user = User.query.get(user_id)
--     if not user:
--         raise ValueError(f"Пользователь с ID {user_id} не найден")
--
--     # Проверка существования курса
--     course = Course.query.get(course_id)
--     if not course:
--         raise ValueError(f"Курс с ID {course_id} не найден")
--
--     # Проверка, не зарегистрирован ли пользователь уже на этот курс
--     existing_enrollment = Enrollment.query.filter_by(
--         user_id=user_id, course_id=course_id).first()
--
--     if existing_enrollment:
--         raise ValueError("Пользователь уже зарегистрирован на этот курс")
--
--     # Регистрация пользователя на курсе
--     enrollment = Enrollment(user_id=user_id, course_id=course_id, progress=0.0)
--     db.session.add(enrollment)
--     db.session.commit()
--
--     return enrollment
