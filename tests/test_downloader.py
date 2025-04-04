import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import aiofiles
import pytest
from m3u8 import M3U8

from async_rutube_downloader.downloader import Downloader
from async_rutube_downloader.settings import (
    TEST_VIDEO_ID,
    URL_FOR_ID_TEMPLATE,
    VIDEO_FORMAT,
    FULL_HD_1080p,
)
from async_rutube_downloader.utils.exceptions import (
    APIResponseError,
    InvalidURLError,
    MasterPlaylistInitializationError,
    QualityError,
)
from async_rutube_downloader.utils.type_hints import APIResponseDict, Qualities
from tests.conftest import RUTUBE_LINK
from tests.utils.validators import is_valid_qualities

# There is few protected methods calls, through mangled names,
# it's not a good practice.


@pytest.mark.asyncio
async def test_download_video(downloader: Downloader, tmp_path: Path) -> None:
    get_calls = 3
    # 3 is _get_api_response, __get_master_playlist, and __get_selected_quality
    downloader._upload_directory = tmp_path
    await downloader.fetch_video_info()
    with patch.object(aiofiles, "open") as aiofiles_open:
        await downloader.download_video()
        aiofiles_open.assert_called_once_with(
            tmp_path / f"{downloader._filename}.{VIDEO_FORMAT}", mode="wb"
        )
        assert (
            downloader._session.get.call_count  # type: ignore
            == len(downloader._selected_quality.segments) + get_calls  # type: ignore
        )


@pytest.mark.asyncio
async def test_download_video_raises_error(downloader: Downloader) -> None:
    with pytest.raises(MasterPlaylistInitializationError):
        await downloader.download_video()


@pytest.mark.asyncio
async def test_select_quality(downloader: Downloader) -> None:
    qualities: Qualities = await downloader.fetch_video_info()
    first_quality = next(iter(qualities))
    assert downloader._selected_quality is None
    await downloader.select_quality(first_quality)
    assert isinstance(downloader._selected_quality, M3U8)


@pytest.mark.asyncio
async def test_select_quality_raise_error_master_playlist_not_initialized(
    downloader: Downloader,
) -> None:
    with pytest.raises(MasterPlaylistInitializationError):
        await downloader.select_quality(FULL_HD_1080p)


@pytest.mark.parametrize(
    "value",
    [
        ("1920", "1080"),
        (1920.0, 1080.0),
        (list(), list()),
        (tuple(), tuple()),
        (dict(), dict()),
        (object, object),
    ],
)
@pytest.mark.asyncio
async def test_validate_selected_quality(
    value: tuple[Any, Any], downloader: Downloader
) -> None:
    with pytest.raises(QualityError):
        await downloader.select_quality(value)


@pytest.mark.asyncio
async def test_fetch_video_info(downloader: Downloader) -> None:
    result = await downloader.fetch_video_info()
    assert is_valid_qualities(result)


@pytest.mark.asyncio
async def test_fetch_video_info_raise_error(
    downloader: Downloader,
    get_response_mock: AsyncMock,
) -> None:
    # Turn off an API response for MasterPlatlist
    get_response_mock.text.side_effect = ""
    with pytest.raises(APIResponseError):
        await downloader.fetch_video_info()


@pytest.mark.parametrize(
    "video_title, expected",
    [
        ("Test Video", "test_video"),
        ("Test Video  -  123", "test_video_123"),
        ("Test Video  -  123  ...", "test_video_123"),
        ("!", "Unknown"),
        ("?", "Unknown"),
        (" ", "Unknown"),
        ("   ", "Unknown"),
        ("видео", "video"),
    ],
)
def test_sanitize_video_title(
    downloader: Downloader,
    video_title: str,
    expected: str,
    api_response_fixture: APIResponseDict,
) -> None:
    api_response_fixture["title"] = video_title
    assert (
        downloader._Downloader__sanitize_video_title(api_response_fixture)  # type: ignore
        == expected
    )


def test_extract_master_playlist_url(
    api_response_fixture: APIResponseDict, downloader: Downloader
) -> None:
    with pytest.raises(
        KeyError, match="M3U8 playlist URL not found in API response."
    ):
        downloader._Downloader__extract_master_playlist_url(  # type: ignore
            {"invalid_key": "invalid_value"}
        )
    assert (
        downloader._Downloader__extract_master_playlist_url(  # type: ignore
            api_response_fixture
        )
        == api_response_fixture["video_balancer"]["m3u8"]
    )


@pytest.mark.asyncio
async def test_get_api_response(
    downloader: Downloader, api_response_fixture: APIResponseDict
) -> None:
    assert await downloader._get_api_response() == api_response_fixture


@pytest.mark.asyncio
async def test_create_downloader(mocked_session: AsyncMock) -> None:
    """Create correct Downloader object."""

    def dummy_callback(arg: int, arg2: int): ...

    loop = asyncio.new_event_loop()

    obj = Downloader(RUTUBE_LINK, loop, dummy_callback, session=mocked_session)

    assert isinstance(obj, Downloader)
    assert obj.url == RUTUBE_LINK
    assert obj._loop == loop
    assert obj._callback == dummy_callback


@pytest.mark.parametrize(
    "wrong_url",
    [
        "",
        " ",
        "\n",
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
        # TODO: "http", and "https", match as the ID.
        # I do not know how short the ID can be .
        "http:",
        "http:/",
        "http://",
        "https:",
        "https:/",
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
    wrong_url: str, mocked_session: AsyncMock
) -> None:
    """
    Test that creating Downloader object with invalid url raises an error.
    """
    with pytest.raises(InvalidURLError):
        Downloader(wrong_url, session=mocked_session)


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
    valid_url: str, mocked_session: AsyncMock
) -> None:
    """
    Test that creating Downloader object with valid url
    does not raise an error.
    """
    assert Downloader(valid_url, session=mocked_session).url == valid_url


def test_downloader_created_with_id(mocked_session: AsyncMock) -> None:
    """
    Test that creating Downloader object with valid url
    does not raise an error.
    """
    assert Downloader(
        TEST_VIDEO_ID, session=mocked_session
    ).url == URL_FOR_ID_TEMPLATE.format(TEST_VIDEO_ID)


def test_interrupt_download(downloader: Downloader) -> None:
    assert downloader.is_interrupted() is False
    downloader.interrupt_download()
    assert downloader.is_interrupted() is True
