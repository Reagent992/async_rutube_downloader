import json
from collections.abc import Callable
from pathlib import Path
from typing import Final
from unittest.mock import AsyncMock, create_autospec

import pytest
from aiohttp import ClientSession

from async_rutube_downloader.downloader import Downloader
from async_rutube_downloader.run_cli import (
    CLIDownloader,
    create_parser,
    parse_args,
)
from async_rutube_downloader.utils.decorators import retry
from async_rutube_downloader.utils.type_hints import APIResponseDict


class RetryTestError(Exception): ...


class RetryTestRaisingError(Exception): ...


RUTUBE_LINK: Final[str] = (
    "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/"
)
RUTUBE_ID: Final[str] = "365ae8f40a2ffd2a5901ace4db799de7"
API_RESPONSE_FIXTURE = Path("tests/fixtures/api_response_fixture.json")
MASTER_PLAYLIST_FIXTURE = Path("tests/fixtures/master_playlist_fixture.m3u8")
VIDEO_FILE_PLAYLIST_FIXTURE = Path(
    "tests/fixtures/video_file_playlist_fixture.mp4.m3u8"
)
CLI_VIDEO_LIST_ENTER = Path("tests/fixtures/videos_list_enter.txt")
# retry decorator
EXCEPTION_TEXT = "exception_text"
EXCEPTION_TO_RAISE = RetryTestError
RETRY_ON_EXCEPTION = RetryTestRaisingError
MAX_RETRIES = 4
RETRY_DELAY = 0.01


@pytest.fixture(scope="function")
def mocked_session() -> AsyncMock:
    """Mocked aiohttp ClientSession."""
    return create_autospec(spec=ClientSession, spec_set=True, instance=True)


@pytest.fixture(scope="function")
def get_response_mock(mocked_session: AsyncMock) -> AsyncMock:
    """Mock `ClientSession.get` method.
    Modify this fixture to return different responses for different tests."""
    get_response_mock = AsyncMock(name="get_method_response_fixture")
    get_response_mock.__aenter__.return_value = get_response_mock
    mocked_session.get.return_value = get_response_mock
    return get_response_mock


@pytest.fixture(scope="session")
def api_response_fixture() -> APIResponseDict:
    """Real json from some Rutube video."""
    with API_RESPONSE_FIXTURE.open() as f:
        return json.load(f)


@pytest.fixture(scope="session")
def master_playlist_fixture() -> str:
    with MASTER_PLAYLIST_FIXTURE.open() as f:
        return f.read()


@pytest.fixture(scope="session")
def video_file_playlist_fixture() -> str:
    with VIDEO_FILE_PLAYLIST_FIXTURE.open() as f:
        return f.read()


@pytest.fixture(scope="function")
def downloader(
    mocked_session: AsyncMock,
    get_response_mock: AsyncMock,
    api_response_fixture: APIResponseDict,
    master_playlist_fixture: str,
    video_file_playlist_fixture: str,
) -> Downloader:
    """Downloader object Fixture with ClientSession and session.get mocked."""
    get_response_mock.json.return_value = api_response_fixture
    get_response_mock.text.side_effect = (
        master_playlist_fixture,
        video_file_playlist_fixture,
    )
    downloader = Downloader(RUTUBE_LINK, session=mocked_session)
    return downloader


@pytest.fixture(scope="function")
def cli_single_url_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    argv = [
        "async_rutube_downloader",
        RUTUBE_ID,
    ]
    monkeypatch.setattr("sys.argv", argv)


@pytest.fixture(scope="function")
def cli_file_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    argv = [
        "async_rutube_downloader",
        "-f",
        str(CLI_VIDEO_LIST_ENTER),
    ]
    monkeypatch.setattr("sys.argv", argv)


@pytest.fixture(scope="function")
def cli_downloader(
    mocked_session: AsyncMock, cli_single_url_fixture: None
) -> CLIDownloader:
    parser = create_parser()
    cli_args = parse_args(parser)
    return CLIDownloader(cli_args, mocked_session)


@pytest.fixture(scope="function")
def retry_decorator_fixture() -> Callable:
    filled_retry_decorator = retry(
        EXCEPTION_TEXT,
        EXCEPTION_TO_RAISE,
        MAX_RETRIES,
        RETRY_DELAY,
        RETRY_ON_EXCEPTION,
    )
    return filled_retry_decorator
