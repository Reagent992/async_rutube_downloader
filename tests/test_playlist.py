from unittest.mock import AsyncMock

import pytest
from m3u8 import M3U8

from src.playlist import MasterPlaylist
from tests.test_utils import validate_qualities
from utils.exceptions import MasterPlaylistInitializationError
from utils.type_hints import APIResponseDict


@pytest.mark.asyncio
async def test_successful_master_playlist_creation(
    mocked_session: AsyncMock,
    get_response_mock: AsyncMock,
    master_playlist_fixture: str,
    api_response_fixture: APIResponseDict,
) -> None:
    get_response_mock.text.return_value = master_playlist_fixture
    master_playlist_url = api_response_fixture["video_balancer"]["m3u8"]
    master_playlist = MasterPlaylist(master_playlist_url, mocked_session)

    with pytest.raises(MasterPlaylistInitializationError):
        master_playlist._MasterPlaylist__get_qualities()  # type: ignore
    assert await master_playlist.run() == master_playlist
    assert isinstance(master_playlist._master_playlist, M3U8)
    get_response_mock.text.assert_awaited_once()
    mocked_session.get.assert_called_once_with(master_playlist_url)
    assert validate_qualities(master_playlist.qualities)
