"""
Конфигурация приложения.
Все константы и настройки вынесены в этот модуль.
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# ============================================================================
# КОНФИГУРАЦИЯ ПОДКЛЮЧЕНИЯ К MYSQL
# ============================================================================

DEFAULT_MYSQL_HOST = 'localhost'
DEFAULT_MYSQL_PORT = 3306
DEFAULT_MYSQL_DATABASE = 'analytics_test'
DEFAULT_MYSQL_USER = 'analytics_user'
DEFAULT_MYSQL_PASSWORD = 'analytics_password'
MYSQL_CONNECTION_TIMEOUT = 10

# Получение настроек из переменных окружения
MYSQL_HOST = os.getenv('MYSQL_HOST', DEFAULT_MYSQL_HOST)
MYSQL_PORT = int(os.getenv('MYSQL_PORT', DEFAULT_MYSQL_PORT))
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', DEFAULT_MYSQL_DATABASE)
MYSQL_USER = os.getenv('MYSQL_USER', DEFAULT_MYSQL_USER)
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', DEFAULT_MYSQL_PASSWORD)

# ============================================================================
# КОНФИГУРАЦИЯ ЗАГРУЗКИ ДАННЫХ
# ============================================================================

GOOGLE_SHEETS_TIMEOUT = 30
BATCH_SIZE = 500
RETRY_MAX_ATTEMPTS = 3
RETRY_DELAY = 1

# ============================================================================
# СТРУКТУРА ДАННЫХ
# ============================================================================

# Обязательные колонки в Google Sheets
REQUIRED_COLUMNS = ['month', 'club_id', 'club_name', 'plan_revenue']

# Статусы загрузки
STATUS_SUCCESS = 'success'
STATUS_PARTIAL = 'partial'
STATUS_FAILED = 'failed'

# ============================================================================
# ВАЛИДАЦИЯ
# ============================================================================

# Невалидные строковые значения
INVALID_STRING_VALUES = ['nan', 'none', '']

# Ограничения
MAX_CLUB_NAME_LENGTH = 255

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

LOG_FILE = 'data_load.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

