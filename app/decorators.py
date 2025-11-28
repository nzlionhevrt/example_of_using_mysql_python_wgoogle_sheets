"""
Декораторы для приложения.
"""

import time
import logging
from functools import wraps
from .config import RETRY_MAX_ATTEMPTS, RETRY_DELAY

logger = logging.getLogger(__name__)


def retry(max_attempts: int = RETRY_MAX_ATTEMPTS, delay: int = RETRY_DELAY):
    """
    Декоратор для retry-логики с экспоненциальной задержкой.
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Базовая задержка в секундах (экспоненциально увеличивается)
    
    Returns:
        Декоратор функции
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Ошибка после {max_attempts} попыток: {e}")
                        raise
                    wait_time = delay * (2 ** attempt)
                    logger.warning(
                        f"Попытка {attempt + 1}/{max_attempts} не удалась: {e}. "
                        f"Повтор через {wait_time} сек..."
                    )
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

