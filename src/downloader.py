import asyncio
import re
import time
from concurrent.futures import Future
from pathlib import Path
from typing import Any, Callable, Final, Optional

import aiofiles
import m3u8
from aiohttp import ClientSession, ClientTimeout

from config import CHUNK_SIZE, LINK, RUTUBE_API_LINK, VIDEO_ID_REGEX
from playlist import MasterPlaylist, Qualities
from utils import (
    APIResponseError,
    InvalidPlaylistError,
    InvalidURLError,
    MasterPlaylistInitializationError,
    UrlDescriptor,
    retry,
)

MINUTE: Final = 60


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
        callback: Optional[Callable[[int, int], None]] = None,
        upload_directory: Path = Path.cwd(),
    ) -> None:
        """
        Args:
            url (str): The URL of the Rutube video to download.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use
                for asynchronous operations.
                Defaults to the current event loop.
            callback (Callable[[int, int], None], optional):
                The callback function to call with the number of
                completed requests and the total requests. Defaults to None.
            upload_directory (Path, optional): The directory to upload
                the video to. Defaults to the current working directory.
        """
        self.url = url
        self.video_title = "Unknown video"
        self._loop = loop
        self._callback = callback
        self._upload_directory = upload_directory
        self._selected_quality: Optional[m3u8.M3U8] = None
        self._master_playlist: Optional[MasterPlaylist] = None
        self._video_id = self.__extract_id_from_url()
        self._timeout = ClientTimeout(
            total=None,
            connect=10,
            sock_connect=10,
            sock_read=MINUTE,
        )
        self._session = ClientSession(
            loop=self._loop, timeout=self._timeout, raise_for_status=True
        )
        self.__amount_of_chunks = 0
        self.__completed_requests = 0
        self.__refresh_rate = 1
        self.__link_to_master_playlist: str = ""

    def fetch_video_info_from_ui(self) -> Future:
        """
        Fetches information about the video from the Rutube API.
        Fill object with video information.
        """
        return asyncio.run_coroutine_threadsafe(
            self._fetch_video_info(), self._loop
        )

    def download_video_from_ui(self) -> Future:
        """
        Downloads the video from the given URL.
        """
        return asyncio.run_coroutine_threadsafe(
            self._download_video(), self._loop
        )

    def select_quality_from_ui(
        self, selected_quality: tuple[int, int]
    ) -> Future:
        return asyncio.run_coroutine_threadsafe(
            self._select_quality(selected_quality), self._loop
        )

    async def _select_quality(self, selected_quality: tuple[int, int]) -> None:
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
        response = await self._session.get(selected_quality_obj.uri)
        self._selected_quality = m3u8.loads(
            await response.text(),
            uri=selected_quality_obj.base_path + "/",
        )
        # selected_quality_obj.base_path
        # doesn't end with "/"" so we need to add it

    async def __select_best_quality(self) -> None:
        if not (
            self._master_playlist is None
            or self._master_playlist.qualities is None
        ):
            max_quality = max(self._master_playlist.qualities.keys())
            await self._select_quality(max_quality)

    @retry("Failed to fetch API response", APIResponseError)
    async def _get_api_response(self) -> dict[str, Any]:
        async with self._session.get(
            RUTUBE_API_LINK.format(self._video_id)
        ) as result:
            return await result.json()

    @retry("Failed to download segment")
    async def _download_segment(self, segment: m3u8.Segment) -> bytes:
        async with self._session.get(segment.absolute_uri) as response:
            self.__completed_requests += 1
            if self._callback:
                await self.__call_callback()
            return await response.read()

    async def _download_video(self) -> None:
        start_time = time.time()
        if not self._selected_quality:
            await self.__select_best_quality()
        segments = list(self._selected_quality.segments)  # type: ignore
        self.__amount_of_chunks = len(segments)
        file_name = f"{self.video_title}.mp4"
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
        print(
            f"Download completed: {self.video_title}\n"
            f"Download completed in {self.total_download_duration} minutes"
        )
        await self._session.close()

    async def _fetch_video_info(self) -> Qualities:
        self.__api_response = await self._get_api_response()
        self.__extract_link_to_master_playlist()
        self.video_title = self.__extract_title()
        self._master_playlist = await MasterPlaylist(
            self.__link_to_master_playlist, self._session
        ).run()
        if self._master_playlist.qualities is not None:
            print("Fetched video title:", self.video_title)
            print(
                "Available qualities:",
                *[
                    f"{index} - {key}"
                    for index, key in enumerate(
                        self._master_playlist.qualities.keys()
                    )
                ],
                sep="\n",
            )
            return self._master_playlist.qualities
        raise

    def __extract_id_from_url(self) -> str:
        if result := re.search(VIDEO_ID_REGEX, self.url):
            return result.group()
        raise InvalidURLError(f"Invalid Rutube URL: {self.url}")

    def __extract_title(self) -> str:
        video_title = self.__api_response.get("title", "Unknown")
        return re.sub(r"[^\w\-_\. ]", "_", video_title)

    def __extract_link_to_master_playlist(self) -> None:
        """Extract url to master playlist from API response."""
        try:
            self.__link_to_master_playlist = self.__api_response[
                "video_balancer"
            ]["m3u8"]
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
            and isinstance(selected_quality[0], int)
            and isinstance(selected_quality[1], int)
            and len(selected_quality) == 2
        ):
            raise TypeError("Quality must be a tuple of two strings")
        return True


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    obj = Downloader(LINK, loop)
    loop.run_until_complete(obj._fetch_video_info())
    # loop.run_until_complete(obj._select_quality((1280, 712)))
    loop.run_until_complete(obj._download_video())
    loop.run_until_complete(obj._session.close())
