import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from tg_bot.core.config import settings


def setup_logging():
    """
    Настройка логирования: вывод в консоль и запись в файл с ротацией.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Форматтер для логов
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    info_handler = TimedRotatingFileHandler(
        "info.log", when="midnight", interval=1, encoding="utf-8"
    )
    info_handler.suffix = "%Y-%m-%d"
    info_handler.setLevel(logging.INFO)

    # Настройка логирования для уровня WARNING и выше
    warning_handler = TimedRotatingFileHandler(
        "warning.log", when="D", interval=7, encoding="utf-8"
    )
    warning_handler.suffix = "%Y-%m-%d"
    warning_handler.setLevel(logging.WARNING)

    # Общая настройка логирования
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)

    # Логгер готов к использованию
    logger.info("Логирование настроено успешно.")
