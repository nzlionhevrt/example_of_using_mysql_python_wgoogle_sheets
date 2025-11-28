"""
Настройка логирования для приложения.
"""

import logging
from .config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

