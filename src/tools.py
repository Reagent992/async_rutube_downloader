import re
from typing import Type

from config import ID_PATTERN, URL_FOR_ID_TEMPLATE, URL_PATTERN


class InvalidURLError(Exception): ...


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
