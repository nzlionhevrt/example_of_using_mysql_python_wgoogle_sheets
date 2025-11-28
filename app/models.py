"""
Модели данных для приложения.
"""

from dataclasses import dataclass
from typing import Optional
from .config import STATUS_SUCCESS, STATUS_PARTIAL, STATUS_FAILED


@dataclass
class LoadResult:
    """Результат загрузки данных."""
    rows_read: int
    rows_inserted: int
    rows_updated: int
    rows_failed: int
    execution_time: float
    status: str
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Проверка успешности загрузки."""
        return self.status == STATUS_SUCCESS

    @property
    def is_partial(self) -> bool:
        """Проверка частичной загрузки."""
        return self.status == STATUS_PARTIAL

