import json
from pathlib import Path
from unittest.mock import AsyncMock, create_autospec

import pytest
from aiohttp import ClientSession

from downloader import Downloader
from utils.type_hints import APIResponseDict

RUTUBE_LINK = "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/"
API_RESPONSE_FIXTURE = Path("tests/fixtures/api_response_fixture.json")
MASTER_PLAYLIST_FIXTURE = Path("tests/fixtures/master_playlist_fixture.m3u8")
VIDEO_FILE_PLAYLIST_FIXTURE = Path(
    "tests/fixtures/video_file_playlist_fixture.mp4.m3u8"
)


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
def url() -> str:
    """Real Rutube URL."""
    return RUTUBE_LINK


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
) -> Downloader:
    """Downloader object Fixture with ClientSession and session.get mocked."""
    get_response_mock.json.return_value = api_response_fixture
    get_response_mock.text.return_value = master_playlist_fixture
    downloader = Downloader(RUTUBE_LINK, session=mocked_session)
    return downloader

