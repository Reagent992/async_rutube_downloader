import logging
from logging.handlers import RotatingFileHandler

from async_rutube_downloader.settings import DEBUG

handlers = []
if DEBUG:
    handlers.append(logging.StreamHandler())
    handlers.append(
        RotatingFileHandler(
            "app.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
        )
    )

logging.basicConfig(
    format="%(asctime)s:%(name)s:%(levelname)s:line %(lineno)d:%(message)s",
    level=logging.INFO,
    handlers=handlers,
)


def get_logger(name: str) -> logging.Logger:
    """Usage: `logger = get_logger(__name__)`"""
    return logging.getLogger(name)
