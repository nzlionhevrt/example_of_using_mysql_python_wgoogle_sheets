"""
Работа с Google Sheets - чтение данных.
"""

import io
import logging
import requests
import pandas as pd
from .decorators import retry
from .config import GOOGLE_SHEETS_TIMEOUT, REQUIRED_COLUMNS, RETRY_MAX_ATTEMPTS, RETRY_DELAY

logger = logging.getLogger(__name__)


class GoogleSheetsReader:
    """Класс для чтения данных из Google Sheets."""
    
    @staticmethod
    def _convert_url_to_csv(sheet_url: str) -> str:
        """
        Преобразует URL Google Sheets в URL для экспорта CSV.
        
        Args:
            sheet_url: URL Google Sheets
        
        Returns:
            URL для экспорта CSV
        """
        if '/edit' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            gid = '0'
            if '#gid=' in sheet_url:
                gid = sheet_url.split('#gid=')[1]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        return sheet_url
    
    @staticmethod
    def _validate_columns(df: pd.DataFrame) -> None:
        """
        Проверяет наличие обязательных колонок в DataFrame.
        
        Args:
            df: DataFrame для проверки
        
        Raises:
            ValueError: Если отсутствуют обязательные колонки
        """
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            error_msg = f"Отсутствуют необходимые колонки: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    @staticmethod
    def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Очищает DataFrame от пустых строк.
        
        Args:
            df: DataFrame для очистки
        
        Returns:
            Очищенный DataFrame
        """
        # Удаляем полностью пустые строки
        df = df.dropna(how='all')
        # Удаляем строки, где все обязательные поля пустые
        df = df.dropna(subset=REQUIRED_COLUMNS, how='all')
        return df
    
    @staticmethod
    @retry(max_attempts=RETRY_MAX_ATTEMPTS, delay=RETRY_DELAY)
    def read(sheet_url: str) -> pd.DataFrame:
        """
        Читает данные из Google Sheets с retry-механизмом.
        
        Args:
            sheet_url: URL Google Sheets
        
        Returns:
            DataFrame с данными
        
        Raises:
            requests.RequestException: При ошибках загрузки
            ValueError: При отсутствии обязательных колонок
        """
        csv_url = GoogleSheetsReader._convert_url_to_csv(sheet_url)
        
        # Загружаем данные с таймаутом через requests
        response = requests.get(csv_url, timeout=GOOGLE_SHEETS_TIMEOUT)
        response.raise_for_status()
        
        # Читаем CSV из строки
        df = pd.read_csv(io.StringIO(response.text))
        
        # Валидация и очистка
        GoogleSheetsReader._validate_columns(df)
        df = GoogleSheetsReader._clean_dataframe(df)
        
        logger.info(f"Успешно прочитано {len(df)} строк из Google Sheets (после фильтрации пустых)")
        return df

