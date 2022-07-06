import logging
from logging.handlers import RotatingFileHandler

from constants import (LOG_COUNT, LOG_DIR, LOG_DT_FORMAT, LOG_ENCODING,
                       LOG_FILE, LOG_FORMAT, LOG_SIZE)


def configure_logging():
    """Инициализация системы логирования."""
    LOG_DIR.mkdir(exist_ok=True)

    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_SIZE, backupCount=LOG_COUNT
    )
    logging.basicConfig(
        datefmt=LOG_DT_FORMAT,
        format=LOG_FORMAT,
        encoding=LOG_ENCODING,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )