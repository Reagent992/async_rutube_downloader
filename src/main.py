import asyncio
import re
import time
from typing import Any

import aiofiles
import m3u8
from aiohttp import ClientError, ClientSession

from config import CHUNK_SIZE, LINK, RUTUBE_API_LINK, VIDEO_ID_REGEX
from playlist import MasterPlaylist
from tools import InvalidURLError, UrlDescriptor


class Downloader:
    """
    Used for downloads a video from a Rutube.

    Args:
        url (str): The URL of the Rutube video to download.
        loop (asyncio.AbstractEventLoop, optional): The event loop to use
            for asynchronous operations. Defaults to the current event loop.
    """

    url = UrlDescriptor()

    def __init__(
        self,
        url: str,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
    ) -> None:
        self.url = url
        self._loop = loop

    async def _get_api_response(
        self,
        session: ClientSession,
        video_id: str,
        max_retries=3,
        retry_delay=0.5,
    ) -> dict[str, Any]:
        for _ in range(max_retries):
            try:
                async with session.get(
                    RUTUBE_API_LINK.format(video_id), raise_for_status=True
                ) as result:
                    return await result.json()
            except ClientError as e:
                print(f"Error fetching API response: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
        raise ClientError(
            f"Failed to fetch API response after {max_retries} retries"
        )

    def extract_video_id(self, url: str) -> str:
        if result := re.search(VIDEO_ID_REGEX, url):
            return result.group()
        raise InvalidURLError(f"Invalid Rutube URL: {url}")

    def extract_title(self, api_response: dict[str, Any]) -> str:
        video_title = api_response.get("title", "Unknown")
        sanitized_title = re.sub(r"[^\w\-_\. ]", "_", video_title)
        return f"{sanitized_title}.mp4"

    async def _download_segment(
        self,
        session: ClientSession,
        segment: m3u8.Segment,
        max_retries=3,
        retry_delay=0.5,
    ) -> bytes:
        for i in range(max_retries):
            try:
                async with session.get(
                    segment.absolute_uri, raise_for_status=True
                ) as response:
                    return await response.read()
            except ClientError as e:
                print(
                    f"Error downloading segment "
                    f"{segment.absolute_uri} (Attempt {i + 1}): {e}"
                )
                await asyncio.sleep(retry_delay)
        raise ClientError(
            f"Failed to download segment {segment.absolute_uri} after retries"
        )

    async def download_video(
        self, stream: m3u8.M3U8, session: ClientSession, video_title: str
    ) -> None:
        segments = list(stream.segments)
        file_name = f"{video_title}.mp4"

        async with aiofiles.open(file_name, mode="wb") as file:
            for i in range(0, len(segments), CHUNK_SIZE):
                download_tasks = [
                    asyncio.create_task(
                        self._download_segment(session, segment)
                    )
                    for segment in segments[i : i + CHUNK_SIZE]
                ]

                downloaded_segments = await asyncio.gather(*download_tasks)

                for segment_data in downloaded_segments:
                    await file.write(segment_data)

    def run(self) -> None:
        self._loop.run_until_complete(self.main())

    async def main(self) -> None:
        start_time = time.time()
        id = self.extract_video_id(self.url)
        async with ClientSession() as session:
            api_response = await self._get_api_response(session, id)
            video_title = self.extract_title(api_response)
            playlist = MasterPlaylist(api_response)
            stream = m3u8.load(playlist.get_best_quality().uri)
            await self.download_video(stream, session, video_title)
            end_time = time.time()
            print(f"Download completed: {video_title}")
            print(
                f"Download completed in "
                f"{(end_time - start_time) / 60:.2f} minutes"
            )


if __name__ == "__main__":
    Downloader(LINK).run()
