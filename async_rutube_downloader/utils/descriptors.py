import re

from async_rutube_downloader.settings import (
    ID_PATTERN,
    URL_FOR_ID_TEMPLATE,
    URL_PATTERN,
)
from async_rutube_downloader.utils.exceptions import InvalidURLError


class UrlDescriptor:
    """
    Descriptor for validating and storing a Rutube video URL.
    """

    def __init__(self, exception: type[Exception] = InvalidURLError) -> None:
        self.exception = exception
        self.id_pattern = ID_PATTERN
        self.url_pattern = URL_PATTERN
        self.url_template = URL_FOR_ID_TEMPLATE

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.private_name = f"_{owner.__name__}__{name}"

    def __get__(self, obj: object, objtype=None) -> str | None:
        return getattr(obj, self.private_name, None)

    def __set__(self, obj: object, value: str) -> None:
        if self.is_valid_url(value):
            setattr(obj, self.private_name, value)
        elif self.is_valid_id(value):
            setattr(obj, self.private_name, self.url_template.format(value))
        else:
            raise self.exception

    def is_valid_url(self, value: str) -> bool:
        return bool(re.fullmatch(self.url_pattern, value))

    def is_valid_id(self, value: str) -> bool:
        return bool(re.fullmatch(self.id_pattern, value))
