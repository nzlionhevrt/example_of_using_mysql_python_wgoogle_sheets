"""
Валидация данных перед загрузкой в БД.
"""

import pandas as pd
from typing import Tuple, Optional, Any
from .config import INVALID_STRING_VALUES, MAX_CLUB_NAME_LENGTH


class DataValidator:
    """Класс для валидации данных."""
    
    @staticmethod
    def is_empty_value(value: Any) -> bool:
        """
        Проверка на пустое значение.
        
        Args:
            value: Значение для проверки
        
        Returns:
            True если значение пустое, False иначе
        """
        if pd.isna(value):
            return True
        str_value = str(value).strip().lower()
        return str_value in INVALID_STRING_VALUES
    
    @staticmethod
    def validate_date(value: Any) -> Tuple[Optional[Any], Optional[str]]:
        """
        Валидация даты. Проверяет, что дата является первым числом месяца.
        
        Args:
            value: Значение для валидации
        
        Returns:
            Кортеж (дата, ошибка). Если валидация успешна, ошибка = None
        """
        if DataValidator.is_empty_value(value):
            return None, "month не может быть пустым"
        
        try:
            date = pd.to_datetime(value).date()
            if date.day != 1:
                return None, f"Дата должна быть первым числом месяца: {value}"
            return date, None
        except Exception as e:
            return None, f"Некорректный формат даты '{value}': {e}"
    
    @staticmethod
    def validate_positive_int(value: Any, field_name: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Валидация положительного целого числа.
        
        Args:
            value: Значение для валидации
            field_name: Имя поля (для сообщения об ошибке)
        
        Returns:
            Кортеж (число, ошибка). Если валидация успешна, ошибка = None
        """
        if DataValidator.is_empty_value(value):
            return None, f"{field_name} не может быть пустым"
        
        try:
            int_value = int(float(value))  # Обработка строк вида "1.0"
            if int_value <= 0:
                return None, f"{field_name} должен быть положительным: {int_value}"
            return int_value, None
        except (ValueError, TypeError) as e:
            return None, f"Некорректный {field_name} '{value}': {e}"
    
    @staticmethod
    def validate_non_negative_float(value: Any, field_name: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Валидация неотрицательного числа с плавающей точкой.
        
        Args:
            value: Значение для валидации
            field_name: Имя поля (для сообщения об ошибке)
        
        Returns:
            Кортеж (число, ошибка). Если валидация успешна, ошибка = None
        """
        if DataValidator.is_empty_value(value):
            return None, f"{field_name} не может быть пустым"
        
        try:
            revenue_str = str(value).replace(' ', '').replace(',', '')
            if revenue_str.lower() in INVALID_STRING_VALUES:
                return None, f"{field_name} не может быть пустым"
            
            float_value = float(revenue_str)
            if float_value < 0:
                return None, f"{field_name} не может быть отрицательным: {float_value}"
            return float_value, None
        except (ValueError, TypeError) as e:
            return None, f"Некорректный {field_name} '{value}': {e}"
    
    @staticmethod
    def validate_string(value: Any, field_name: str, max_length: int = MAX_CLUB_NAME_LENGTH) -> Tuple[Optional[str], Optional[str]]:
        """
        Валидация строки.
        
        Args:
            value: Значение для валидации
            field_name: Имя поля (для сообщения об ошибке)
            max_length: Максимальная длина строки
        
        Returns:
            Кортеж (строка, ошибка). Если валидация успешна, ошибка = None
        """
        if DataValidator.is_empty_value(value):
            return None, f"{field_name} не может быть пустым"
        
        str_value = str(value).strip()
        if len(str_value) > max_length:
            return None, f"{field_name} слишком длинный ({len(str_value)} символов, максимум {max_length})"
        
        return str_value, None

