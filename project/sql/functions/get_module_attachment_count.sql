-- Функция для подсчета количества вложений в модуле
CREATE OR REPLACE FUNCTION get_module_attachment_count(module_id_param INTEGER)
RETURNS INTEGER AS $$
DECLARE
    attachment_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO attachment_count
    FROM attachments
    WHERE module_id = module_id_param;

    RETURN COALESCE(attachment_count, 0);
END;
$$ LANGUAGE plpgsql;

-- Для SQLite:
-- Поскольку SQLite не поддерживает создание хранимых функций через SQL напрямую,
-- мы будем использовать эту функцию через Python.
-- Функция будет реализована в Python-коде как:
--
-- def get_module_attachment_count(module_id):
--     query = "SELECT COUNT(*) FROM attachments WHERE module_id = ?"
--     result = db.session.execute(query, (module_id,)).scalar()
--     return result or 0
