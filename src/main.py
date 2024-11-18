import asyncio
import re
import time
from typing import Any

import aiofiles
import m3u8
from aiohttp import ClientError, ClientSession

from config import CHUNK_SIZE, RUTUBE_API_LINK, VIDEO_ID_REGEX, LINK
from playlist import MasterPlaylist


async def _get_api_response(
    session: ClientSession,
    video_id: str,
    max_retries=3,
    retry_delay=0.5,
) -> dict[str, Any]:
    for i in range(max_retries):
        try:
            async with session.get(
                RUTUBE_API_LINK.format(video_id), raise_for_status=True
            ) as result:
                return await result.json()
        except ClientError as e:
            print(f"Error fetching API response: {e}")
            await asyncio.sleep(retry_delay)
    raise ClientError(
        f"Failed to fetch API response after {max_retries} retries"
    )


def extract_video_id(url: str) -> str:
    if result := re.search(VIDEO_ID_REGEX, url):
        return result.group()
    raise ValueError(f"Invalid Rutube URL: {url}")


def extract_title(api_response: dict[str, Any]) -> str:
    video_title = api_response.get("title", "Unknown")
    sanitized_title = re.sub(r"[^\w\-_\. ]", "_", video_title)
    return f"{sanitized_title}.mp4"


async def _download_segment(
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
    stream: m3u8.M3U8, session: ClientSession, video_title: str
) -> None:
    segments = list(stream.segments)
    file_name = f"{video_title}.mp4"

    async with aiofiles.open(file_name, mode="wb") as file:
        for i in range(0, len(segments), CHUNK_SIZE):
            download_tasks = [
                asyncio.create_task(_download_segment(session, segment))
                for segment in segments[i : i + CHUNK_SIZE]
            ]

            downloaded_segments = await asyncio.gather(*download_tasks)

            for segment_data in downloaded_segments:
                await file.write(segment_data)


async def main(link: str = LINK) -> None:
    try:
        id = extract_video_id(link)
        async with ClientSession() as session:
            api_response = await _get_api_response(session, id)
            video_title = extract_title(api_response)
            playlist = MasterPlaylist(api_response)
            stream = m3u8.load(playlist.get_best_quality().uri)
            await download_video(stream, session, video_title)
            print(f"Download completed: {video_title}")
    except Exception as e:
        print(f"Unexpected error during video download: {e}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Download completed in {(end_time - start_time) / 60:.2f} minutes")
