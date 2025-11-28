-- SQL запрос для создания объединенного датасета в DataLens
-- Объединяет данные из revenue_plan и sales_fact (FULL OUTER JOIN через UNION)
-- Включает поле месяца в формате "Название месяца\год"

SELECT 
    COALESCE(rp.month, sf.sale_date) AS date,
    -- Форматирование месяца в формате "Название месяца\год" (русский)
    CONCAT(
        CASE MONTH(COALESCE(rp.month, sf.sale_date))
            WHEN 1 THEN 'Январь'
            WHEN 2 THEN 'Февраль'
            WHEN 3 THEN 'Март'
            WHEN 4 THEN 'Апрель'
            WHEN 5 THEN 'Май'
            WHEN 6 THEN 'Июнь'
            WHEN 7 THEN 'Июль'
            WHEN 8 THEN 'Август'
            WHEN 9 THEN 'Сентябрь'
            WHEN 10 THEN 'Октябрь'
            WHEN 11 THEN 'Ноябрь'
            WHEN 12 THEN 'Декабрь'
        END,
        '\\',
        YEAR(COALESCE(rp.month, sf.sale_date))
    ) AS month_name_year,
    COALESCE(rp.club_id, sf.club_id) AS club_id,
    COALESCE(rp.club_name, sf.club_name) AS club_name,
    IFNULL(rp.plan_revenue, 0) AS plan_revenue,
    IFNULL(sf.revenue, 0) AS fact_revenue,
    IFNULL(sf.contracts_count, 0) AS contracts_count
FROM revenue_plan rp
LEFT JOIN sales_fact sf ON (rp.club_id = sf.club_id AND rp.month = sf.sale_date)

UNION

SELECT 
    sf.sale_date AS date,
    -- Форматирование месяца в формате "Название месяца\год" (русский)
    CONCAT(
        CASE MONTH(sf.sale_date)
            WHEN 1 THEN 'Январь'
            WHEN 2 THEN 'Февраль'
            WHEN 3 THEN 'Март'
            WHEN 4 THEN 'Апрель'
            WHEN 5 THEN 'Май'
            WHEN 6 THEN 'Июнь'
            WHEN 7 THEN 'Июль'
            WHEN 8 THEN 'Август'
            WHEN 9 THEN 'Сентябрь'
            WHEN 10 THEN 'Октябрь'
            WHEN 11 THEN 'Ноябрь'
            WHEN 12 THEN 'Декабрь'
        END,
        '\\',
        YEAR(sf.sale_date)
    ) AS month_name_year,
    sf.club_id,
    sf.club_name,
    0 AS plan_revenue,
    sf.revenue AS fact_revenue,
    sf.contracts_count
FROM sales_fact sf
WHERE NOT EXISTS (
    SELECT 1 FROM revenue_plan rp 
    WHERE rp.club_id = sf.club_id AND rp.month = sf.sale_date
)
ORDER BY date, club_id;

