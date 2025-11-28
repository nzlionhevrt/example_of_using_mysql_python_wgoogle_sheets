-- Создание базы данных (если еще не создана)
CREATE DATABASE IF NOT EXISTS analytics_test;
USE analytics_test;

-- Создание таблицы факта продаж
CREATE TABLE IF NOT EXISTS sales_fact (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sale_date       DATE NOT NULL,
    club_id         INT NOT NULL,
    club_name       VARCHAR(255) NOT NULL,
    revenue         DECIMAL(12,2) NOT NULL,
    contracts_count INT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Создание таблицы плана выручки
CREATE TABLE IF NOT EXISTS revenue_plan (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    month        DATE NOT NULL,
    club_id      INT NOT NULL,
    club_name    VARCHAR(255) NOT NULL,
    plan_revenue DECIMAL(12,2) NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_month_club (month, club_id)
);

-- Создание таблицы для логирования загрузок
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

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_sales_fact_date_club 
    ON sales_fact(sale_date, club_id);
    
CREATE INDEX IF NOT EXISTS idx_revenue_plan_month_club 
    ON revenue_plan(month, club_id);

-- Заполнение тестовыми данными для sales_fact (минимум 3 клуба)
INSERT INTO sales_fact (sale_date, club_id, club_name, revenue, contracts_count, created_at, updated_at) VALUES
('2025-09-01', 1, 'Club A', 4500000.00, 120, NOW(), NOW()),
('2025-10-01', 1, 'Club A', 3200000.00, 85, NOW(), NOW()),
('2025-11-01', 1, 'Club A', 5100000.00, 135, NOW(), NOW()),
('2025-09-01', 2, 'Club B', 3800000.00, 95, NOW(), NOW()),
('2025-10-01', 2, 'Club B', 4200000.00, 110, NOW(), NOW()),
('2025-11-01', 2, 'Club B', 3600000.00, 90, NOW(), NOW()),
('2025-09-01', 3, 'Club C', 3200000.00, 80, NOW(), NOW()),
('2025-10-01', 3, 'Club C', 2900000.00, 72, NOW(), NOW()),
('2025-11-01', 3, 'Club C', 3400000.00, 88, NOW(), NOW())
ON DUPLICATE KEY UPDATE updated_at = NOW();

