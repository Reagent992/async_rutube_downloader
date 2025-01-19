import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from aiohttp import ClientError

from utils.logger import get_logger

logger = get_logger(__name__)

Function = TypeVar("Function", bound=Callable[..., Awaitable[Any]])


def retry(
    exception_text: str,
    exception_to_raise: type[Exception] = ClientError,
    max_retries: int = 3,
    retry_delay: float = 0.5,
    retry_on_exception: type[Exception] = ClientError,
) -> Callable[[Function], Function]:
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
        retry_on_exception (type[Exception], optional):
            The exception class that will trigger a retry.
            Defaults to ClientError.
    """

    def decorator(func: Function) -> Function:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for _ in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except retry_on_exception as e:
                    logger.info(
                        f"Connection error: {e} - "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    await asyncio.sleep(retry_delay)
            raise exception_to_raise(exception_text)

        return wrapper  # type: ignore

    return decorator
