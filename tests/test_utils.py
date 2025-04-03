from typing import Any, Callable
from unittest.mock import AsyncMock

import m3u8
import pytest

from async_rutube_downloader.utils.type_hints import (
    Qualities,
    QualitiesWithPlaylist,
)
from tests.conftest import (
    EXCEPTION_TEXT,
    EXCEPTION_TO_RAISE,
    MAX_RETRIES,
    RETRY_ON_EXCEPTION,
)


@pytest.mark.asyncio
async def test_retry_just_work(retry_decorator_fixture: Callable):
    mock_for_calling = AsyncMock()
    test_arg = "some_test_text"
    await retry_decorator_fixture(mock_for_calling)(test_arg)
    mock_for_calling.assert_called_once_with(test_arg)


@pytest.mark.asyncio
async def test_retry_raise_error(retry_decorator_fixture: Callable):
    mock_for_calling = AsyncMock()
    mock_for_calling.side_effect = RETRY_ON_EXCEPTION
    with pytest.raises(EXCEPTION_TO_RAISE, match=EXCEPTION_TEXT):
        await retry_decorator_fixture(mock_for_calling)()
    assert mock_for_calling.call_count == MAX_RETRIES


def is_valid_qualities(qualities: Qualities | Any) -> bool:
    """
    Validate the qualities dictionary.
    Qualities should be tuple[tuple[int, int], ...]
    """
    if not isinstance(qualities, tuple):
        return False
    for width, high in qualities:
        if not (isinstance(width, int) and isinstance(high, int)):
            return False
    return True


def is_valid_qualities_with_playlist(
    qualities: QualitiesWithPlaylist | Any,
) -> bool:
    """
    Validate the qualities dictionary.
    Qualities should be dict[tuple[int, int], m3u8.Playlist]
    """
    if not isinstance(qualities, dict):
        return False
    for key, value in qualities.items():
        if not (
            isinstance(key, tuple)
            and len(key) == 2
            and all(isinstance(i, int) for i in key)
        ):
            return False
        if not isinstance(value, m3u8.Playlist):
            return False
    return True
