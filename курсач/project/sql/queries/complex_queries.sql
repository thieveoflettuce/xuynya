-- 1. Запрос с JOIN и WHERE: получение активных пользователей с их курсами
-- (пользователи, которые зарегистрированы хотя бы на один курс)
SELECT
    u.id AS user_id,
    u.name AS user_name,
    u.email,
    COUNT(e.id) AS enrolled_courses,
    MAX(e.enrollment_date) AS last_enrollment_date
FROM
    users u
JOIN
    enrollments e ON u.id = e.user_id
WHERE
    u.role = 'student'
GROUP BY
    u.id, u.name, u.email
HAVING
    COUNT(e.id) > 0
ORDER BY
    COUNT(e.id) DESC;

-- 2. Запрос с JOIN, WHERE и HAVING: получение популярных курсов с количеством записавшихся и средним рейтингом
SELECT
    c.id AS course_id,
    c.title AS course_title,
    COUNT(e.id) AS enrollment_count,
    AVG(f.rating) AS average_rating
FROM
    courses c
LEFT JOIN
    enrollments e ON c.id = e.course_id
LEFT JOIN
    feedbacks f ON c.id = f.course_id
GROUP BY
    c.id, c.title
HAVING
    COUNT(e.id) >= 5 AND AVG(f.rating) > 3.5
ORDER BY
    enrollment_count DESC, average_rating DESC;

-- 3. Запрос с JOIN, WHERE и GROUP BY: получение статистики по модулям для каждого курса
SELECT
    c.id AS course_id,
    c.title AS course_title,
    COUNT(m.id) AS module_count,
    COUNT(a.id) AS assessment_count,
    AVG(a.grade) AS average_grade
FROM
    courses c
LEFT JOIN
    modules m ON c.id = m.course_id
LEFT JOIN
    assessments a ON m.id = a.module_id
WHERE
    c.created_at > date('now', '-1 year')
GROUP BY
    c.id, c.title
ORDER BY
    module_count DESC, average_grade DESC;

-- 4. Запрос с вычисляемыми полями: получение статистики успеваемости пользователей
SELECT
    u.id AS user_id,
    u.name AS user_name,
    COUNT(a.id) AS completed_assessments,
    AVG(a.grade) AS average_grade,
    (AVG(a.grade) / 5.0) * 100 AS performance_percentage,
    CASE
        WHEN AVG(a.grade) >= 4.5 THEN 'Отлично'
        WHEN AVG(a.grade) >= 3.5 THEN 'Хорошо'
        WHEN AVG(a.grade) >= 2.5 THEN 'Удовлетворительно'
        ELSE 'Неудовлетворительно'
    END AS performance_category
FROM
    users u
LEFT JOIN
    assessments a ON u.id = a.user_id
WHERE
    u.role = 'student'
GROUP BY
    u.id, u.name
ORDER BY
    average_grade DESC;

-- 5. Запрос с вычисляемыми полями: получение статистики по курсам
SELECT
    c.id AS course_id,
    c.title AS course_title,
    COUNT(m.id) AS module_count,
    COUNT(DISTINCT e.user_id) AS student_count,
    (COUNT(DISTINCT e.user_id) * 100.0 / (SELECT COUNT(*) FROM users WHERE role = 'student')) AS enrollment_percentage,
    AVG(f.rating) AS average_rating,
    (AVG(f.rating) / 5.0) * 100 AS satisfaction_percentage
FROM
    courses c
LEFT JOIN
    modules m ON c.id = m.course_id
LEFT JOIN
    enrollments e ON c.id = e.course_id
LEFT JOIN
    feedbacks f ON c.id = f.course_id
GROUP BY
    c.id, c.title
ORDER BY
    student_count DESC, average_rating DESC;

-- 6. Запрос с вычисляемыми полями: получение статистики активности пользователей
SELECT
    u.id AS user_id,
    u.name AS user_name,
    COUNT(e.id) AS enrolled_courses,
    COUNT(a.id) AS completed_assessments,
    (COUNT(a.id) * 1.0 / NULLIF((SELECT COUNT(m.id) FROM modules m JOIN enrollments e2 ON m.course_id = e2.course_id WHERE e2.user_id = u.id), 0)) * 100 AS completion_rate,
    AVG(e.progress) AS average_progress,
    AVG(f.rating) AS average_feedback
FROM
    users u
LEFT JOIN
    enrollments e ON u.id = e.user_id
LEFT JOIN
    assessments a ON u.id = a.user_id
LEFT JOIN
    feedbacks f ON u.id = f.user_id
WHERE
    u.role = 'student'
GROUP BY
    u.id, u.name
ORDER BY
    completion_rate DESC, average_progress DESC;
