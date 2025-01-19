import logging
from logging.handlers import RotatingFileHandler

from settings import DEBUG

logging.basicConfig(
    format="%(asctime)s:%(name)s:%(levelname)s:line %(lineno)d:%(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            "app.log",
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Usage: `logger = get_logger(__name__)`"""
    new_logger = logging.getLogger(name)
    if DEBUG:
        new_logger.setLevel(logging.DEBUG)
    return new_logger
