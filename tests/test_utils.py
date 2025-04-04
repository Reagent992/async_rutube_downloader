from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

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
