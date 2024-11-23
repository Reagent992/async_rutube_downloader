import asyncio
import re
from functools import wraps
from typing import Callable, Type

from aiohttp import ClientError

from config import ID_PATTERN, URL_FOR_ID_TEMPLATE, URL_PATTERN


class InvalidURLError(Exception):
    """Wrong RuTube URL passed. So there is nothing to download."""


class NoQualitySelectedError(Exception): ...


class APIResponseError(Exception): ...


class MasterPlaylistInitializationError(Exception):
    """Exception for rare situation when MasterPlaylist object is created
    but, run method is not called."""


class UrlDescriptor:
    """
    Descriptor for validating and storing a Rutube video URL.
    """

    def __init__(self, exception=InvalidURLError) -> None:
        self.exception = exception
        self.id_pattern = ID_PATTERN
        self.url_pattern = URL_PATTERN
        self.url_template = URL_FOR_ID_TEMPLATE

    def __set_name__(self, owner: Type[object], name: str):
        self.private_name = f"_{owner.__name__}__{name}"

    def __get__(self, obj: object, objtype=None):
        return getattr(obj, self.private_name, None)

    def __set__(self, obj: object, value: str) -> None:
        if self.full_url_validator(value):
            setattr(obj, self.private_name, value)
        elif self.just_id_validator(value):
            setattr(obj, self.private_name, self.url_template.format(value))
        else:
            raise self.exception

    def full_url_validator(self, value: str) -> bool:
        return bool(re.fullmatch(self.url_pattern, value))

    def just_id_validator(self, value: str) -> bool:
        return bool(re.fullmatch(self.id_pattern, value))


def retry(
    exception_text: str,
    exception_to_raise: Type[Exception] = ClientError,
    max_retries=3,
    retry_delay=0.5,
    retry_on_exception: Type[Exception] = ClientError,
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
                    print(
                        f"Connection error: {e}\n"
                        f"Retrying in {retry_delay} seconds..."
                    )
                    await asyncio.sleep(retry_delay)
            raise exception_to_raise(exception_text)

        return wrapper

    return decorator
