import asyncio
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar, cast

from aiohttp import ClientError

from async_rutube_downloader.utils.logger import get_logger

logger = get_logger(__name__)

AsyncFunc = TypeVar("AsyncFunc", bound=Callable[..., Awaitable[Any]])


def retry(
    exception_text: str,
    exception_to_raise: type[Exception] = ClientError,
    max_retries: int = 3,
    retry_delay: float = 0.5,
    retry_on_exception: type[Exception] = ClientError,
) -> Callable[[AsyncFunc], AsyncFunc]:
    """
    Decorator that calls a function multiple times
    if it raises an exception.
    If there are no more retries, raise the specified exception .

    Args:
        exception_text (str):
            The text of the exception that will be raised
            after max_retries attempts.
        exception_to_raise (type[Exception], optional):
            The exception class to raise after max_retries
            attempts. Defaults to ClientError.
        max_retries (int, optional):
            The maximum number of attempts. Defaults to 3.
        retry_delay (float, optional):
            The delay between attempts in seconds. Defaults to 0.5.
            The actual delay increases with each attempt as
            (retry_delay * iteration).
        retry_on_exception (type[Exception], optional):
            The exception class that will trigger a retry.
            Defaults to ClientError.
    """

    def decorator(func: AsyncFunc) -> AsyncFunc:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for iteration in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on_exception as e:
                    logger.info(
                        "Connection error: %s - Retrying in %s seconds...",
                        e,
                        retry_delay * iteration,
                    )
                    await asyncio.sleep(retry_delay * iteration)
            logger.info("Failed to connect after %s attempts.", max_retries)
            raise exception_to_raise(exception_text)

        return cast(AsyncFunc, wrapper)

    return decorator


def log_download_time(func: AsyncFunc) -> AsyncFunc:
    """Simply tracks the function work time and logs it."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        total_seconds = round(end_time - start_time)
        minutes, seconds = divmod(total_seconds, 60)
        logger.info("Downloaded in %s minutes, %s seconds", minutes, seconds)
        return result

    return cast(AsyncFunc, wrapper)
