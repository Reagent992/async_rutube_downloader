import ssl
from asyncio import AbstractEventLoop

import certifi
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from async_rutube_downloader.utils.miscellaneous import get_or_create_loop


def create_aiohttp_session(
    loop: AbstractEventLoop | None = None,
) -> ClientSession:
    """
    Creating an aiohttp session with preset timeouts.
    If the event loop is not passed, a new one will be created.
    """
    if not loop:
        loop = get_or_create_loop()
    session_timeout = ClientTimeout(
        total=None,
        # The video may be really long,
        # and one session can be used for multiple videos.
        connect=5,
        sock_connect=5,  # 5 seconds to setup a TCP connection.
        sock_read=60 * 3,
        # Chunks are small in size,
        # so 3 minutes should be enough to download one chunk.
    )

    # Fixes [SSL: CERTIFICATE_VERIFY_FAILED] in PyInstaller builds,
    # especially on GitHub Actions, where system CA certs may be missing.
    # certifi provides a portable CA bundle for reliable HTTPS.
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = TCPConnector(ssl=ssl_context, loop=loop)
    return ClientSession(
        loop=loop,
        timeout=session_timeout,
        connector=connector,
        raise_for_status=True,
    )
