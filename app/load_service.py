"""
Сервис для загрузки данных из Google Sheets в MySQL.
"""

import time
import logging
from typing import Optional
from .config import STATUS_SUCCESS, STATUS_PARTIAL, STATUS_FAILED, BATCH_SIZE
from .models import LoadResult
from .google_sheets import GoogleSheetsReader
from .database import DatabaseManager, RevenuePlanLoader

logger = logging.getLogger(__name__)


class DataLoadService:
    """Сервис для загрузки данных."""
    
    @staticmethod
    def _determine_status(rows_read: int, failed: int) -> str:
        """
        Определяет статус загрузки.
        
        Args:
            rows_read: Количество прочитанных строк
            failed: Количество ошибок
        
        Returns:
            Статус загрузки
        """
        if failed == 0:
            return STATUS_SUCCESS
        elif failed < rows_read:
            return STATUS_PARTIAL
        return STATUS_FAILED
    
    @staticmethod
    def load_data(sheet_url: str) -> LoadResult:
        """
        Основной метод загрузки данных.
        
        Args:
            sheet_url: URL Google Sheets
        
        Returns:
            Результат загрузки
        
        Raises:
            Exception: При критических ошибках загрузки
        """
        start_time = time.time()
        connection = None
        
        try:
            # Чтение данных из Google Sheets
            logger.info("Чтение данных из Google Sheets...")
            df = GoogleSheetsReader.read(sheet_url)
            rows_read = len(df)
            logger.info(f"Прочитано {rows_read} строк")
            
            # Подключение к MySQL
            logger.info("Подключение к MySQL...")
            connection = DatabaseManager.get_connection()
            logger.info("Подключение установлено")
            
            # Создание таблицы логов
            DatabaseManager.create_log_table(connection)
            
            # Выполнение UPSERT
            logger.info("Выполнение UPSERT...")
            inserted, updated, failed = RevenuePlanLoader.load(connection, df, BATCH_SIZE)
            
            # Расчет времени выполнения
            execution_time = round(time.time() - start_time, 2)
            status = DataLoadService._determine_status(rows_read, failed)
            
            result = LoadResult(
                rows_read=rows_read,
                rows_inserted=inserted,
                rows_updated=updated,
                rows_failed=failed,
                execution_time=execution_time,
                status=status
            )
            
            # Логирование результата
            DatabaseManager.log_load_result(connection, result, sheet_url)
            
            return result
            
        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            error_msg = str(e)
            logger.error(f"Критическая ошибка: {error_msg}")
            
            result = LoadResult(
                rows_read=0,
                rows_inserted=0,
                rows_updated=0,
                rows_failed=0,
                execution_time=execution_time,
                status=STATUS_FAILED,
                error_message=error_msg
            )
            
            # Сохранение ошибки в лог
            if connection:
                try:
                    DatabaseManager.log_load_result(connection, result, sheet_url)
                except:
                    pass
            
            raise
        finally:
            if connection:
                connection.close()
                logger.info("Соединение с MySQL закрыто")

