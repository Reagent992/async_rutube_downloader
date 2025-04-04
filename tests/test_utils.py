from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

from async_rutube_downloader.settings import FULL_HD_1080p, HD_720p
from async_rutube_downloader.utils.validators import is_quality_valid
from tests.conftest import (
    EXCEPTION_TEXT,
    EXCEPTION_TO_RAISE,
    MAX_RETRIES,
    RETRY_ON_EXCEPTION,
)


@pytest.mark.asyncio
async def test_retry_just_work(retry_decorator_fixture: Callable) -> None:
    mock_for_calling = AsyncMock()
    test_arg = "some_test_text"
    await retry_decorator_fixture(mock_for_calling)(test_arg)
    mock_for_calling.assert_called_once_with(test_arg)


@pytest.mark.asyncio
async def test_retry_raise_error(retry_decorator_fixture: Callable) -> None:
    mock_for_calling = AsyncMock()
    mock_for_calling.side_effect = RETRY_ON_EXCEPTION
    with pytest.raises(EXCEPTION_TO_RAISE, match=EXCEPTION_TEXT):
        await retry_decorator_fixture(mock_for_calling)()
    assert mock_for_calling.call_count == MAX_RETRIES


@pytest.mark.parametrize(
    "quality",
    (
        (1, 1),
        FULL_HD_1080p,
        HD_720p,
    ),
)
def test_is_quality_valid(quality) -> None:
    assert is_quality_valid(quality)


@pytest.mark.parametrize(
    "quality",
    (
        None,
        "",
        "1920x720",
        123,
        (0, 0),
        (1920, "720"),
        (-1, -1),
        ("", ""),
        ("1920", "720"),
        ((1, 1), (1, 1)),
        (1, 2, 3),
    ),
)
def test_is_quality_invalid(quality) -> None:
    assert is_quality_valid(quality) is False
