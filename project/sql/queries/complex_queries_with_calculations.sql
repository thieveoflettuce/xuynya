-- Файл с комплексными запросами, включающими вычисляемые поля

-- 1. Запрос для получения статистики по вложениям для модулей
-- Вычисляемые поля: total_size_mb, avg_size_kb, size_per_enrollment_kb
SELECT
    m.id AS module_id,
    m.title AS module_title,
    c.id AS course_id,
    c.title AS course_title,
    COUNT(a.id) AS attachment_count,
    SUM(a.file_size) AS total_size,
    ROUND(SUM(a.file_size) / (1024.0 * 1024.0), 2) AS total_size_mb,
    ROUND(AVG(a.file_size) / 1024.0, 2) AS avg_size_kb,
    ROUND(SUM(a.file_size) / (1024.0 * NULLIF(COUNT(DISTINCT e.user_id), 0)), 2) AS size_per_enrollment_kb
FROM
    modules m
JOIN
    courses c ON m.course_id = c.id
LEFT JOIN
    attachments a ON m.id = a.module_id
LEFT JOIN
    enrollments e ON c.id = e.course_id
GROUP BY
    m.id, m.title, c.id, c.title
HAVING
    COUNT(a.id) > 0
ORDER BY
    COUNT(a.id) DESC, total_size_mb DESC;

-- 2. Запрос для получения статистики по активности пользователей
-- Вычисляемые поля: completion_rate, activity_score, engagement_level
SELECT
    u.id AS user_id,
    u.name AS user_name,
    u.email AS user_email,
    COUNT(DISTINCT e.course_id) AS enrolled_courses,
    COUNT(DISTINCT a.module_id) AS completed_modules,
    ROUND((COUNT(DISTINCT a.module_id) * 100.0) / NULLIF((
        SELECT COUNT(m.id) FROM modules m
        JOIN enrollments e2 ON m.course_id = e2.course_id
        WHERE e2.user_id = u.id
    ), 0), 2) AS completion_rate,
    ROUND(AVG(e.progress), 2) AS avg_progress,
    ROUND(AVG(f.rating), 2) AS avg_rating,
    ROUND(
        (COUNT(DISTINCT e.course_id) * 0.2) +
        (AVG(COALESCE(f.rating, 0)) * 0.3) +
        (AVG(COALESCE(e.progress, 0)) * 0.5)
    , 2) AS activity_score,
    CASE
        WHEN (COUNT(DISTINCT e.course_id) * 0.2) +
             (AVG(COALESCE(f.rating, 0)) * 0.3) +
             (AVG(COALESCE(e.progress, 0)) * 0.5) >= 4 THEN 'Высокий'
        WHEN (COUNT(DISTINCT e.course_id) * 0.2) +
             (AVG(COALESCE(f.rating, 0)) * 0.3) +
             (AVG(COALESCE(e.progress, 0)) * 0.5) >= 2.5 THEN 'Средний'
        ELSE 'Низкий'
    END AS engagement_level
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
    u.id, u.name, u.email
ORDER BY
    activity_score DESC;

-- 3. Запрос для получения статистики по эффективности курсов
-- Вычисляемые поля: avg_time_to_complete_days, completion_rate, effectiveness_score
SELECT
    c.id AS course_id,
    c.title AS course_title,
    COUNT(DISTINCT m.id) AS module_count,
    COUNT(DISTINCT e.user_id) AS enrolled_users,
    COUNT(DISTINCT e.id) FILTER (WHERE e.progress = 100) AS completed_enrollments,
    ROUND(
        AVG(
            JULIANDAY(e.last_accessed) - JULIANDAY(e.enrollment_date)
        ) FILTER (WHERE e.progress = 100)
    , 2) AS avg_time_to_complete_days,
    ROUND(
        (COUNT(DISTINCT e.id) FILTER (WHERE e.progress = 100) * 100.0) /
        NULLIF(COUNT(DISTINCT e.id), 0)
    , 2) AS completion_rate,
    ROUND(AVG(COALESCE(f.rating, 0)), 2) AS avg_rating,
    ROUND(
        (
            (COUNT(DISTINCT e.id) FILTER (WHERE e.progress = 100) * 100.0) /
            NULLIF(COUNT(DISTINCT e.id), 0) * 0.6
        ) +
        (
            AVG(COALESCE(f.rating, 0)) * 0.4
        )
    , 2) AS effectiveness_score
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
    effectiveness_score DESC;
