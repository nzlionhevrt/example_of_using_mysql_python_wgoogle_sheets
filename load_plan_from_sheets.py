#!/usr/bin/env python3
"""
Скрипт для загрузки данных плана выручки из Google Sheets в MySQL.
Выполняет UPSERT: обновляет существующие записи или вставляет новые.

Использование:
    python load_plan_from_sheets.py

Требования:
    - Файл .env с настройками подключения к MySQL и URL Google Sheets
    - Установленные зависимости из requirements.txt
"""

import os
import sys
import logging
from app.logger_config import logger
from app.load_service import DataLoadService

# Настройка логирования уже выполнена в logger_config


def main():
    """Основная функция."""
    sheet_url = os.getenv('GOOGLE_SHEETS_URL')
    
    if not sheet_url:
        error_msg = "Не указан GOOGLE_SHEETS_URL в .env файле"
        logger.error(error_msg)
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Начало загрузки данных из Google Sheets")
    logger.info(f"Источник: {sheet_url}")
    
    try:
        result = DataLoadService.load_data(sheet_url)
        
        logger.info("=" * 60)
        logger.info(f"Загрузка завершена за {result.execution_time} секунд")
        logger.info(f"Статус: {result.status}")
        logger.info(
            f"Обработано: {result.rows_inserted} новых, "
            f"{result.rows_updated} обновлено, {result.rows_failed} ошибок"
        )
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Загрузка завершилась с ошибкой: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
