# Критичные улучшения сбора данных

## 1. Обработка ошибок и надежность ⚠️ КРИТИЧНО

### Проблемы:
- Нет retry-механизма при сбоях сети (Google Sheets может быть временно недоступен)
- Нет обработки таймаутов подключения к MySQL
- При ошибке одной строки теряется информация о других строках

### Решения:
- ✅ Добавить retry-логику с экспоненциальной задержкой (3 попытки)
- ✅ Добавить таймауты для всех сетевых операций (30 сек для Google Sheets, 10 сек для MySQL)
- ✅ Продолжать обработку при ошибках отдельных строк (не прерывать весь процесс)

**Пример реализации:**
```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # экспоненциальная задержка
            return None
        return wrapper
    return decorator
```

## 2. Валидация данных ⚠️ КРИТИЧНО

### Проблемы:
- Нет проверки диапазонов значений (отрицательные суммы, некорректные ID)
- Нет проверки формата дат
- Нет проверки на NULL значения

### Решения:
- ✅ Валидация формата даты (должна быть первым числом месяца)
- ✅ Проверка диапазонов: `plan_revenue >= 0`, `club_id > 0`
- ✅ Проверка на NULL значения в обязательных полях
- ✅ Валидация длины строковых полей (`club_name` не более 255 символов)

**Пример валидации:**
```python
def validate_row(row):
    errors = []
    
    # Проверка даты
    try:
        date = pd.to_datetime(row['month']).date()
        if date.day != 1:
            errors.append(f"Дата должна быть первым числом месяца: {row['month']}")
    except:
        errors.append(f"Некорректный формат даты: {row['month']}")
    
    # Проверка club_id
    try:
        club_id = int(row['club_id'])
        if club_id <= 0:
            errors.append(f"club_id должен быть положительным: {club_id}")
    except:
        errors.append(f"Некорректный club_id: {row['club_id']}")
    
    # Проверка plan_revenue
    try:
        revenue = float(str(row['plan_revenue']).replace(' ', '').replace(',', ''))
        if revenue < 0:
            errors.append(f"plan_revenue не может быть отрицательным: {revenue}")
    except:
        errors.append(f"Некорректный plan_revenue: {row['plan_revenue']}")
    
    # Проверка club_name
    if pd.isna(row['club_name']) or str(row['club_name']).strip() == '':
        errors.append("club_name не может быть пустым")
    elif len(str(row['club_name'])) > 255:
        errors.append(f"club_name слишком длинный: {len(str(row['club_name']))}")
    
    return errors
```

## 3. Логирование ⚠️ КРИТИЧНО

### Проблемы:
- Только вывод в консоль, нет структурированного логирования
- Нет истории загрузок
- Нет метрик для анализа проблем

### Решения:
- ✅ Использовать библиотеку `logging` с записью в файл
- ✅ Логировать метрики: время выполнения, количество обработанных строк, ошибки
- ✅ Создать таблицу `data_load_log` для истории загрузок

**SQL для таблицы логов:**
```sql
CREATE TABLE IF NOT EXISTS data_load_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    load_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_url VARCHAR(500),
    rows_read INT DEFAULT 0,
    rows_inserted INT DEFAULT 0,
    rows_updated INT DEFAULT 0,
    rows_failed INT DEFAULT 0,
    execution_time_seconds DECIMAL(10,2),
    status ENUM('success', 'partial', 'failed') DEFAULT 'success',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_load_date (load_date),
    INDEX idx_status (status)
);
```

**Пример использования:**
```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_load.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## 4. Производительность ⚠️ КРИТИЧНО

### Проблемы:
- Построчная обработка (медленно для больших объемов)
- Нет индексов для оптимизации запросов
- Нет batch-вставок

### Решения:
- ✅ Использовать `executemany()` для batch-вставок вместо цикла
- ✅ Добавить индексы для ускорения JOIN и поиска
- ✅ Использовать транзакции с оптимальным размером batch (500 строк)

**SQL для индексов:**
```sql
-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_sales_fact_date_club 
    ON sales_fact(sale_date, club_id);
    
CREATE INDEX IF NOT EXISTS idx_revenue_plan_month_club 
    ON revenue_plan(month, club_id);
```

**Пример batch-обработки:**
```python
def upsert_revenue_plan_batch(connection, df, batch_size=500):
    cursor = connection.cursor()
    
    upsert_query = """
    INSERT INTO revenue_plan (month, club_id, club_name, plan_revenue, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        club_name = VALUES(club_name),
        plan_revenue = VALUES(plan_revenue),
        updated_at = VALUES(updated_at)
    """
    
    now = datetime.now()
    batch = []
    
    for _, row in df.iterrows():
        try:
            month = pd.to_datetime(row['month']).date()
            club_id = int(row['club_id'])
            club_name = str(row['club_name']).strip()
            plan_revenue = float(str(row['plan_revenue']).replace(' ', '').replace(',', ''))
            
            batch.append((month, club_id, club_name, plan_revenue, now, now))
            
            if len(batch) >= batch_size:
                cursor.executemany(upsert_query, batch)
                connection.commit()
                batch = []
        except Exception as e:
            logger.error(f"Ошибка обработки строки: {e}")
            continue
    
    # Обработать оставшиеся записи
    if batch:
        cursor.executemany(upsert_query, batch)
        connection.commit()
    
    cursor.close()
```

## 5. Исправление SQL запроса для DataLens ⚠️ КРИТИЧНО

### Проблема:
В `datalens_query.sql` используется `CROSS JOIN` с условием `ON`, что неправильно. MySQL не поддерживает `FULL OUTER JOIN`, нужно использовать `UNION`.

### Решение:
Исправить запрос на корректный `LEFT JOIN` + `UNION` для эмуляции `FULL OUTER JOIN`.

**Исправленный запрос:**
```sql
SELECT 
    COALESCE(rp.month, sf.sale_date) AS date,
    CONCAT(
        CASE MONTH(COALESCE(rp.month, sf.sale_date))
            WHEN 1 THEN 'Январь' WHEN 2 THEN 'Февраль' WHEN 3 THEN 'Март'
            WHEN 4 THEN 'Апрель' WHEN 5 THEN 'Май' WHEN 6 THEN 'Июнь'
            WHEN 7 THEN 'Июль' WHEN 8 THEN 'Август' WHEN 9 THEN 'Сентябрь'
            WHEN 10 THEN 'Октябрь' WHEN 11 THEN 'Ноябрь' WHEN 12 THEN 'Декабрь'
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
    CONCAT(
        CASE MONTH(sf.sale_date)
            WHEN 1 THEN 'Январь' WHEN 2 THEN 'Февраль' WHEN 3 THEN 'Март'
            WHEN 4 THEN 'Апрель' WHEN 5 THEN 'Май' WHEN 6 THEN 'Июнь'
            WHEN 7 THEN 'Июль' WHEN 8 THEN 'Август' WHEN 9 THEN 'Сентябрь'
            WHEN 10 THEN 'Октябрь' WHEN 11 THEN 'Ноябрь' WHEN 12 THEN 'Декабрь'
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
```

## Приоритет внедрения

1. **Срочно:** Исправление SQL запроса (пункт 5)
2. **Высокий:** Обработка ошибок (пункт 1)
3. **Высокий:** Валидация данных (пункт 2)
4. **Высокий:** Производительность - batch обработка (пункт 4)
5. **Средний:** Логирование (пункт 3)
