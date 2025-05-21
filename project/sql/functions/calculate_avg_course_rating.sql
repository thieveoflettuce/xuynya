-- Функция для вычисления среднего рейтинга курса
CREATE OR REPLACE FUNCTION calculate_avg_course_rating(course_id_param INTEGER)
RETURNS FLOAT AS $$
DECLARE
    avg_rating FLOAT;
BEGIN
    SELECT AVG(rating) INTO avg_rating
    FROM feedbacks
    WHERE course_id = course_id_param;

    RETURN COALESCE(avg_rating, 0);
END;
$$ LANGUAGE plpgsql;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых функций через SQL напрямую,
-- мы будем использовать эту функцию через Python.
-- Функция будет реализована в Python-коде как:
--
-- def calculate_avg_course_rating(course_id):
--     query = "SELECT AVG(rating) FROM feedbacks WHERE course_id = ?"
--     result = db.session.execute(query, (course_id,)).scalar()
--     return result or 0
