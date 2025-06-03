import asyncio
import re
from collections.abc import Callable
from pathlib import Path

import aiofiles
import m3u8
from aiofiles.threadpool.binary import AsyncBufferedIOBase
from aiohttp import ClientSession
from slugify import slugify

from async_rutube_downloader.playlist import MasterPlaylist
from async_rutube_downloader.settings import (
    CHUNK_SIZE,
    RUTUBE_API_LINK,
    VIDEO_FORMAT,
    VIDEO_ID_REGEX,
)
from async_rutube_downloader.utils.create_session import create_aiohttp_session
from async_rutube_downloader.utils.decorators import log_download_time, retry
from async_rutube_downloader.utils.descriptors import UrlDescriptor
from async_rutube_downloader.utils.exceptions import (
    APIResponseError,
    InvalidPlaylistError,
    InvalidURLError,
    M3U8URLNotFoundError,
    MasterPlaylistInitializationError,
    QualityError,
    SegmentDownloadError,
)
from async_rutube_downloader.utils.interfaces import DownloaderABC
from async_rutube_downloader.utils.logger import get_logger
from async_rutube_downloader.utils.miscellaneous import (
    get_or_create_loop,
    resolve_file_name,
)
from async_rutube_downloader.utils.type_hints import APIResponseDict, Qualities
from async_rutube_downloader.utils.validators import is_quality_valid

logger = get_logger(__name__)


class Downloader(DownloaderABC):
    """
    Downloads a video from Rutube using the URL
    and saves it to a file in a specified folder.
    """

    url = UrlDescriptor()

    def __init__(
        self,
        url: str,
        loop: asyncio.AbstractEventLoop | None = None,
        callback: Callable[[int, int], None] | None = None,
        upload_directory: Path = Path.cwd(),
        session: ClientSession | None = None,
        auto_close_session: bool = True,
    ) -> None:
        """
        Args:
            url: The URL of the Rutube video to download.
            loop: The event loop to use
                for asynchronous operations.
                Defaults to the current event loop.
            callback:
                The callback function to call with the number of
                completed requests and the total requests. Defaults to None.
            upload_directory: The directory to upload
                the video to. Defaults to the current working directory.
            session: The aiohttp ClientSession to use for requests.
            auto_close_session: Whether to close the session
        """
        self.url = url
        self.video_title = "Unknown video"
        self._filename = "Unknown video"
        self._loop = loop if loop else get_or_create_loop()
        self._callback = callback
        self._upload_directory = upload_directory
        self._selected_quality: m3u8.M3U8 | None = None
        self._master_playlist: MasterPlaylist | None = None
        self._video_id = self.__extract_id_from_url()
        self._session = (
            session if session else create_aiohttp_session(self._loop)
        )
        self._auto_close_session = auto_close_session
        self.__api_response: APIResponseDict | None = None
        self.__total_chunks = 0
        self.__completed_requests = 0
        self.__refresh_rate = 1
        self.__master_playlist_url: str = ""
        self.__download_cancelled = False

    async def fetch_video_info(self) -> Qualities:
        """Fetch video info from Rutube API."""
        self.__api_response = await self._get_api_response()
        self.__master_playlist_url = self.__extract_master_playlist_url(
            self.__api_response
        )
        self.video_title = self.__api_response.get("title", "Unknown")
        self._filename = self.__sanitize_video_title(self.__api_response)
        self._master_playlist = await MasterPlaylist(
            self.__master_playlist_url, self._session
        ).run()
        if self._master_playlist.qualities is not None:
            return tuple(self._master_playlist.qualities.keys())
        raise APIResponseError

    async def select_quality(self, selected_quality: tuple[int, int]) -> None:
        """
        Selects the quality of the video to download.

        Args:
            selected_quality: A tuple of two integers representing the
                width and height of the video quality to download.
        """
        if not is_quality_valid(selected_quality):
            raise QualityError
        if (
            self._master_playlist is None
            or self._master_playlist.qualities is None
        ):
            raise MasterPlaylistInitializationError
        selected_quality_obj = self._master_playlist.qualities[
            selected_quality
        ]
        if not selected_quality_obj.uri:
            raise InvalidPlaylistError
        self._selected_quality = await self.__get_selected_quality(
            selected_quality_obj.uri
        )

    @log_download_time
    async def download_video(self) -> None:
        """
        Asynchronously downloads a video by fetching its segments
        and writing them to a file.

        This method selects the best quality for the video
        if not already selected, divides the video into segments,
        and downloads each segment concurrently. The downloaded segments are
        then written to a file in the specified upload directory.
        """
        if self._master_playlist is None:
            raise MasterPlaylistInitializationError
        if self._selected_quality is None:
            await self.__select_best_quality()
        assert self._selected_quality
        self.segments = self._selected_quality.segments
        self.__total_chunks = len(self.segments)
        self.__refresh_rate = len(self.segments) // self.__total_chunks
        self.file = resolve_file_name(
            self._upload_directory, self._filename, VIDEO_FORMAT
        )

        async with aiofiles.open(
            self.file,
            mode="wb",
        ) as file:
            await self._download_video(file)

        if self._auto_close_session:
            await self.close_session()

    async def _download_video(self, file: AsyncBufferedIOBase) -> None:
        for i in range(0, len(self.segments), CHUNK_SIZE):
            if not self.__download_cancelled:
                download_tasks = [
                    asyncio.create_task(self._download_segment(segment))
                    for segment in self.segments[i : i + CHUNK_SIZE]
                ]
                downloaded_segments = await asyncio.gather(*download_tasks)
                await file.writelines(downloaded_segments)
            else:
                break

    def interrupt_download(self) -> None:
        """Will stop the next chunk of video segments from downloading."""
        logger.info("Download is cancelled")
        self.__download_cancelled = True

    def is_interrupted(self) -> bool:
        return self.__download_cancelled

    async def close_session(self) -> None:
        if not self._session.closed:
            await self._session.close()

    @retry("Failed to fetch API response", APIResponseError)
    async def _get_api_response(self) -> APIResponseDict:
        """Actually going to Rutube API and fetching video info by id."""
        async with self._session.get(
            RUTUBE_API_LINK.format(self._video_id)
        ) as result:
            return await result.json()

    @retry("Failed to download segment of video", SegmentDownloadError)
    async def _download_segment(self, segment: m3u8.Segment) -> bytes:
        async with self._session.get(segment.absolute_uri) as response:
            self.__completed_requests += 1
            if self._callback:
                await self.__call_callback()
            return await response.read()

    async def __select_best_quality(self) -> None:
        if not (
            self._master_playlist is None
            or self._master_playlist.qualities is None
        ):
            max_quality = max(self._master_playlist.qualities.keys())
            await self.select_quality(max_quality)

    def __sanitize_video_title(self, api_response: APIResponseDict) -> str:
        result = slugify(api_response.get("title", "Unknown"), separator="_")
        return result if result else "Unknown"

    def __extract_id_from_url(self) -> str:
        if self.url and (result := re.search(VIDEO_ID_REGEX, self.url)):
            return result.group()
        raise InvalidURLError(self.url)

    def __extract_master_playlist_url(
        self, api_response: APIResponseDict
    ) -> str:
        """Extract url to master playlist from API response."""
        try:
            return api_response["video_balancer"]["m3u8"]
        except KeyError:
            raise M3U8URLNotFoundError

    async def __call_callback(self) -> None:
        """Once we've completed 1% of requests, call
        the callback with the number of completed
        requests and the total requests."""
        if self._callback and (
            self.__completed_requests % self.__refresh_rate == 0
            or self.__completed_requests == self.__total_chunks
        ):
            self._callback(self.__completed_requests, self.__total_chunks)

    @retry("Failed to fetch API response", APIResponseError)
    async def __get_selected_quality(self, quality_url: str) -> m3u8.M3U8:
        async with self._session.get(quality_url) as response:
            return m3u8.loads(await response.text(), quality_url)
