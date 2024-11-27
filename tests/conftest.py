from typing import LiteralString
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientSession


@pytest.fixture
def url() -> LiteralString:
    """Real Rutube URL."""
    return "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/"


@pytest.fixture
def mock_session():
    """
    Fixture to mock aiohttp.ClientSession.
    """
    with patch("aiohttp.ClientSession") as mock_session:
        # Mock the context manager for `ClientSession`
        mock_session.return_value.__aenter__.return_value = AsyncMock(
            spec=ClientSession
        )
        yield mock_session
