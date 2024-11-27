import asyncio
from typing import LiteralString

import pytest

from config import URL_FOR_ID_TEMPLATE
from src.downloader import Downloader
from src.utils import InvalidURLError


def test_create_downloader(url: LiteralString) -> None:
    """Create correct Downloader object."""

    def dummy_callback(arg: int, arg2: int): ...

    loop = asyncio.new_event_loop()

    obj = Downloader(url, loop, dummy_callback)

    assert isinstance(obj, Downloader)
    assert obj.url == url
    assert obj._loop == loop
    assert obj._callback == dummy_callback


@pytest.mark.parametrize(
    "wrong_url",
    [
        "",
        "/",
        "ےے",
        "їј",
        "ø",
        "α",
        "𝒜",
        "үяҒғ",
        "èéêëì",
        "абв",
        "ÎÏÐÑÒÓÔ",
        "https://",
        "https://rutube.ru/",
        "https://rutube.ru/video/",
        "https://rutube.ru/video/abc-123/extra",
        "https://example.com/video/abc123",
        "https://rutube.ru/page/12345",
        "http://rutube.com/video/12345",
        "https://rutube.ru/videos/abc123",
        "https://rutube.ru/videos/abc123?id=12345",
        "https://rutube.ru/video/abc123#description",
        "https://rutube.ru/video/abc 123",
        "rutube.ru/video/abc_123/extra",
        "https://rutube.ru/vid/abc123",
        "https://rutube.ru/video/abc!123",
        "rutube.com/video/12345",
        "https://rutube.ru/abc123",
        "https://rutube.ru/video/abc/12345",
        "https://rutube.ru/video/abc-123/extra/",
        "https://www.rutube.ru/video/abc123",
    ],
)
def test_create_downloader_with_invalid_url(
    wrong_url: str,
) -> None:
    """
    Test that creating Downloader object with invalid url raises an error.
    """
    with pytest.raises(InvalidURLError):
        Downloader(wrong_url)


@pytest.mark.parametrize(
    "valid_url",
    [
        "rutube.ru/video/2ce725b3dc1a243f8456458975ecd872",
        "rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/",
        "http://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872",
        "http://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/",
        "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872",
        "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/",
    ],
)
def test_downloader_created_with_valid_url(
    valid_url: str,
) -> None:
    """
    Test that creating Downloader object with valid url does not raise an error.
    """
    assert Downloader(valid_url).url == valid_url


def test_downloader_created_with_id() -> None:
    """
    Test that creating Downloader object with valid url does not raise an error.
    """
    video_id = "2ce725b3dc1a243f8456458975ecd872"
    assert Downloader(video_id).url == URL_FOR_ID_TEMPLATE.format(video_id)
