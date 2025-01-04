import asyncio
from collections.abc import Callable
from functools import wraps

from aiohttp import ClientError

from utils.logger import get_logger

logger = get_logger(__name__)


def retry(
    exception_text: str,
    exception_to_raise: type[Exception] = ClientError,
    max_retries: int = 3,
    retry_delay: float = 0.5,
    retry_on_exception: type[Exception] = ClientError,
):
    """Decorator that call a function multiple times
    if it raises an exception."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except retry_on_exception as e:
                    logger.info(
                        f"Connection error: {e}\n"
                        f"Retrying in {retry_delay} seconds..."
                    )
                    await asyncio.sleep(retry_delay)
            raise exception_to_raise(exception_text)

        return wrapper

    return decorator
