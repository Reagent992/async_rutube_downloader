import asyncio
import re
import time
from collections.abc import Callable
from pathlib import Path

import aiofiles
import m3u8
from aiohttp import ClientSession
from slugify import slugify

from playlist import MasterPlaylist, Qualities
from settings import (
    CHUNK_SIZE,
    MINUTE,
    RUTUBE_API_LINK,
    TEST_VIDEO_URL,
    VIDEO_ID_REGEX,
)
from utils.create_session import create_aiohttp_session
from utils.decorators import retry
from utils.descriptors import UrlDescriptor
from utils.exceptions import (
    APIResponseError,
    InvalidPlaylistError,
    InvalidURLError,
    MasterPlaylistInitializationError,
    QualityError,
    SegmentDownloadError,
)
from utils.logger import get_logger
from utils.type_hints import APIResponseDict

logger = get_logger(__name__)


class Downloader:
    """
    Downloads a video from Rutube using the URL
    and saves it to a file in a specified folder.
    """

    url = UrlDescriptor()

    def __init__(
        self,
        url: str,
        loop: asyncio.AbstractEventLoop = asyncio.new_event_loop(),
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
        self._loop = loop
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
        self.__amount_of_chunks = 0
        self.__completed_requests = 0
        self.__refresh_rate = 1
        self.__master_playlist_url: str = ""

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
            return self._master_playlist.qualities
        raise APIResponseError

    async def select_quality(self, selected_quality: tuple[int, int]) -> None:
        """
        Selects the quality of the video to download.

        Args:
            selected_quality: A tuple of two integers representing the
                width and height of the video quality to download.
        """
        self.__validate_selected_quality(selected_quality)
        if (
            self._master_playlist is None
            or self._master_playlist.qualities is None
        ):
            raise MasterPlaylistInitializationError(
                "Master playlist is not initialized, call run() method first"
            )
        selected_quality_obj = self._master_playlist.qualities[
            selected_quality
        ]
        if not selected_quality_obj.uri:
            raise InvalidPlaylistError("Invalid playlist selected")
        self._selected_quality = await self.__get_selected_quality(
            selected_quality_obj.uri
        )

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
        start_time = time.time()
        if self._selected_quality is None:
            await self.__select_best_quality()
        assert self._selected_quality
        segments = self._selected_quality.segments
        self.__amount_of_chunks = len(segments)
        file_name = f"{self._filename}.mp4"
        self.__refresh_rate = len(segments) // self.__amount_of_chunks

        async with aiofiles.open(
            self._upload_directory / file_name, mode="wb"
        ) as file:
            for i in range(0, len(segments), CHUNK_SIZE):
                download_tasks = [
                    asyncio.create_task(self._download_segment(segment))
                    for segment in segments[i : i + CHUNK_SIZE]
                ]
                downloaded_segments = await asyncio.gather(*download_tasks)
                await file.writelines(downloaded_segments)

        end_time = time.time()
        self.total_download_duration = round(
            (end_time - start_time) / MINUTE, 1
        )
        logger.info(
            f"Downloaded {self.video_title} in "
            f"{self.total_download_duration} minutes"
        )
        if self._auto_close_session:
            await self.close()

    async def close(self) -> None:
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
        raise InvalidURLError(f"Invalid Rutube URL: {self.url}")

    def __extract_master_playlist_url(
        self, api_response: APIResponseDict
    ) -> str:
        """Extract url to master playlist from API response."""
        try:
            return api_response["video_balancer"]["m3u8"]
        except KeyError:
            raise KeyError("M3U8 playlist URL not found in API response.")

    async def __call_callback(self) -> None:
        """Once we've completed 1% of requests, call
        the callback with the number of completed
        requests and the total requests."""
        if self._callback and (
            self.__completed_requests % self.__refresh_rate == 0
            or self.__completed_requests == self.__amount_of_chunks
        ):
            self._callback(self.__completed_requests, self.__amount_of_chunks)

    @staticmethod
    def __validate_selected_quality(selected_quality: tuple[int, int]) -> bool:
        if not (
            isinstance(selected_quality, tuple)
            and len(selected_quality) == 2
            and all(isinstance(i, int) for i in selected_quality)
        ):
            raise QualityError("Quality must be a tuple of two integers.")
        return True

    @retry("Failed to fetch API response", APIResponseError)
    async def __get_selected_quality(self, quality_url: str) -> m3u8.M3U8:
        async with self._session.get(quality_url) as response:
            return m3u8.loads(await response.text(), quality_url)


if __name__ == "__main__":

    async def main(loop):
        downloader = Downloader(TEST_VIDEO_URL, loop=loop)
        await downloader.fetch_video_info()
        # await downloader.select_quality((1920, 1080))
        await downloader.download_video()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
