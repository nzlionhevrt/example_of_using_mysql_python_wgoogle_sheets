"""
Работа с базой данных MySQL.
"""

import sys
import logging
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Any, Callable
from .config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD,
    MYSQL_CONNECTION_TIMEOUT
)
from .models import LoadResult

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Класс для работы с базой данных."""
    
    @staticmethod
    def get_connection() -> mysql.connector.MySQLConnection:
        """
        Создает подключение к MySQL с таймаутами.
        
        Returns:
            Подключение к MySQL
        
        Exits:
            sys.exit(1): При ошибке подключения
        """
        try:
            return mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                database=MYSQL_DATABASE,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                connection_timeout=MYSQL_CONNECTION_TIMEOUT,
                autocommit=False
            )
        except Error as e:
            logger.error(f"Ошибка подключения к MySQL: {e}")
            sys.exit(1)
    
    @staticmethod
    def execute_with_cursor(connection: mysql.connector.MySQLConnection, 
                          operation: Callable, 
                          *args, **kwargs) -> Any:
        """
        Выполняет операцию с автоматическим управлением курсором.
        
        Args:
            connection: Подключение к БД
            operation: Функция для выполнения (принимает cursor первым аргументом)
            *args: Позиционные аргументы для operation
            **kwargs: Именованные аргументы для operation
        
        Returns:
            Результат выполнения operation
        """
        cursor = connection.cursor()
        try:
            return operation(cursor, *args, **kwargs)
        finally:
            cursor.close()
    
    @staticmethod
    def create_log_table(connection: mysql.connector.MySQLConnection) -> None:
        """
        Создает таблицу для логирования загрузок, если её нет.
        
        Args:
            connection: Подключение к БД
        """
        def _create_table(cursor):
            cursor.execute("""
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
                )
            """)
            connection.commit()
            logger.info("Таблица data_load_log готова")
        
        try:
            DatabaseManager.execute_with_cursor(connection, _create_table)
        except Error as e:
            logger.warning(f"Не удалось создать таблицу data_load_log: {e}")
    
    @staticmethod
    def log_load_result(connection: mysql.connector.MySQLConnection, 
                       result: LoadResult, 
                       source_url: str) -> None:
        """
        Сохраняет результат загрузки в таблицу логов.
        
        Args:
            connection: Подключение к БД
            result: Результат загрузки
            source_url: URL источника данных
        """
        def _insert_log(cursor):
            cursor.execute("""
                INSERT INTO data_load_log 
                (source_url, rows_read, rows_inserted, rows_updated, rows_failed, 
                 execution_time_seconds, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                source_url, result.rows_read, result.rows_inserted, 
                result.rows_updated, result.rows_failed,
                result.execution_time, result.status, result.error_message
            ))
            connection.commit()
        
        try:
            DatabaseManager.execute_with_cursor(connection, _insert_log)
        except Error as e:
            logger.warning(f"Не удалось сохранить лог загрузки: {e}")


class RevenuePlanLoader:
    """Класс для загрузки данных плана выручки."""
    
    UPSERT_QUERY = """
        INSERT INTO revenue_plan (month, club_id, club_name, plan_revenue, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            club_name = VALUES(club_name),
            plan_revenue = VALUES(plan_revenue),
            updated_at = VALUES(updated_at)
    """
    
    @staticmethod
    def _process_batch(cursor: mysql.connector.cursor.MySQLCursor, 
                      batch: list, 
                      connection: mysql.connector.MySQLConnection) -> None:
        """
        Обрабатывает batch данных.
        
        Args:
            cursor: Курсор БД
            batch: Список данных для вставки
            connection: Подключение к БД
        """
        cursor.executemany(RevenuePlanLoader.UPSERT_QUERY, batch)
        connection.commit()
        logger.debug(f"Обработан batch из {len(batch)} строк")
    
    @staticmethod
    def _calculate_updated_count(cursor: mysql.connector.cursor.MySQLCursor, 
                                start_time: datetime) -> int:
        """
        Подсчитывает количество обновленных записей (приблизительно).
        
        Args:
            cursor: Курсор БД
            start_time: Время начала загрузки
        
        Returns:
            Количество обновленных записей
        """
        cursor.execute("""
            SELECT COUNT(*) FROM revenue_plan 
            WHERE updated_at >= %s AND updated_at <= %s
        """, (start_time, datetime.now()))
        return cursor.fetchone()[0]
    
    @staticmethod
    def load(connection: mysql.connector.MySQLConnection, 
            df: 'pd.DataFrame', 
            batch_size: int = 500) -> tuple:
        """
        Выполняет UPSERT данных в таблицу revenue_plan с batch-обработкой.
        
        Args:
            connection: Подключение к БД
            df: DataFrame с данными
            batch_size: Размер batch для обработки
        
        Returns:
            Кортеж (inserted_count, updated_count, failed_count)
        
        Raises:
            Error: При ошибках выполнения запросов
        """
        import pandas as pd
        from .transformers import DataTransformer
        
        cursor = connection.cursor()
        inserted_count = 0
        updated_count = 0
        failed_count = 0
        batch = []
        start_time = datetime.now()
        
        try:
            for idx, row in df.iterrows():
                # Преобразование и валидация строки
                data, error = DataTransformer.transform_row(row)
                
                if error:
                    failed_count += 1
                    logger.warning(f"Строка {idx + 1} не прошла валидацию: {error}")
                    logger.debug(f"Данные строки: {row.to_dict()}")
                    continue
                
                batch.append(data)
                
                # Выполняем batch при достижении размера
                if len(batch) >= batch_size:
                    RevenuePlanLoader._process_batch(cursor, batch, connection)
                    inserted_count += len(batch)
                    batch = []
            
            # Обработать оставшиеся записи
            if batch:
                RevenuePlanLoader._process_batch(cursor, batch, connection)
                inserted_count += len(batch)
            
            # Подсчет обновленных записей (приблизительный)
            total_updated = RevenuePlanLoader._calculate_updated_count(cursor, start_time)
            updated_count = max(0, total_updated - inserted_count)
            
            logger.info(
                f"Успешно обработано: {inserted_count} новых записей, "
                f"{updated_count} обновлено, {failed_count} ошибок"
            )
            
            return inserted_count, updated_count, failed_count
            
        except Error as e:
            connection.rollback()
            logger.error(f"Ошибка выполнения UPSERT: {e}")
            raise
        finally:
            cursor.close()

