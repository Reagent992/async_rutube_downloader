import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path

from aiohttp import ClientSession

from async_rutube_downloader.utils.descriptors import UrlDescriptor
from async_rutube_downloader.utils.type_hints import Qualities


class DownloaderABC(ABC):
    url: str | UrlDescriptor  # it's a nightmare to typehint Descriptor
    video_title: str

    @abstractmethod
    def __init__(
        self,
        url: str,
        loop: asyncio.AbstractEventLoop | None = None,
        callback: Callable[[int, int], None] | None = None,
        upload_directory: Path = Path.cwd(),
        session: ClientSession | None = None,
        auto_close_session: bool = True,
    ) -> None: ...

    @abstractmethod
    async def fetch_video_info(self) -> Qualities: ...

    @abstractmethod
    async def download_video(self): ...

    @abstractmethod
    async def select_quality(
        self, selected_quality: tuple[int, int]
    ) -> None: ...

    @abstractmethod
    def interrupt_download(self) -> None: ...

    @abstractmethod
    def is_interrupted(self) -> bool: ...

    @abstractmethod
    async def close_session(self) -> None: ...
