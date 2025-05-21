-- Функция для вычисления прогресса пользователя по курсу
CREATE OR REPLACE FUNCTION calculate_user_progress(user_id_param INTEGER, course_id_param INTEGER)
RETURNS FLOAT AS $$
DECLARE
    total_modules INTEGER;
    completed_assessments INTEGER;
    progress_percentage FLOAT;
BEGIN
    -- Подсчет общего количества модулей в курсе
    SELECT COUNT(*) INTO total_modules
    FROM modules
    WHERE course_id = course_id_param;

    -- Подсчет количества выполненных модулей (имеющих оценки)
    SELECT COUNT(DISTINCT a.module_id) INTO completed_assessments
    FROM assessments a
    JOIN modules m ON a.module_id = m.id
    WHERE a.user_id = user_id_param AND m.course_id = course_id_param AND a.grade > 0;

    -- Вычисление процента прогресса
    IF total_modules > 0 THEN
        progress_percentage := (completed_assessments::FLOAT / total_modules::FLOAT) * 100;
    ELSE
        progress_percentage := 0;
    END IF;

    RETURN progress_percentage;
END;
$$ LANGUAGE plpgsql;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых функций через SQL напрямую,
-- мы будем использовать эту функцию через Python.
-- Функция будет реализована в Python-коде как:
--
-- def calculate_user_progress(user_id, course_id):
--     # Подсчет общего количества модулей в курсе
--     total_modules = db.session.query(func.count(Module.id)).\
--         filter(Module.course_id == course_id).scalar() or 0
--
--     # Подсчет количества выполненных модулей (имеющих оценки)
--     completed_assessments = db.session.query(func.count(func.distinct(Assessment.module_id))).\
--         join(Module, Assessment.module_id == Module.id).\
--         filter(Assessment.user_id == user_id,
--                Module.course_id == course_id,
--                Assessment.grade > 0).scalar() or 0
--
--     # Вычисление процента прогресса
--     if total_modules > 0:
--         progress_percentage = (completed_assessments / total_modules) * 100
--     else:
--         progress_percentage = 0
--
--     return progress_percentage
