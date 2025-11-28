"""
Преобразование данных из строки в нужный формат для БД.
"""

import pandas as pd
from datetime import datetime
from typing import Tuple, Optional
from .validators import DataValidator


class DataTransformer:
    """Класс для преобразования данных из строки в нужный формат."""
    
    @staticmethod
    def transform_row(row: pd.Series) -> Tuple[Optional[Tuple], Optional[str]]:
        """
        Преобразует строку данных в кортеж для вставки в БД.
        
        Args:
            row: Строка данных из DataFrame
        
        Returns:
            Кортеж (данные, ошибка). 
            Если преобразование успешно: (кортеж данных, None)
            Если ошибка: (None, строка с ошибками)
        """
        errors = []
        
        # Валидация и преобразование даты
        month, error = DataValidator.validate_date(row.get('month'))
        if error:
            errors.append(error)
        
        # Валидация и преобразование club_id
        club_id, error = DataValidator.validate_positive_int(row.get('club_id'), 'club_id')
        if error:
            errors.append(error)
        
        # Валидация и преобразование club_name
        club_name, error = DataValidator.validate_string(row.get('club_name'), 'club_name')
        if error:
            errors.append(error)
        
        # Валидация и преобразование plan_revenue
        plan_revenue, error = DataValidator.validate_non_negative_float(row.get('plan_revenue'), 'plan_revenue')
        if error:
            errors.append(error)
        
        if errors:
            return None, ', '.join(errors)
        
        now = datetime.now()
        return (month, club_id, club_name, plan_revenue, now, now), None

