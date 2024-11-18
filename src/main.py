import asyncio
import re
import time
from typing import Any, Final

import aiofiles
import m3u8
from aiohttp import ClientError, ClientSession

from config import CHUNK_SIZE, RUTUBE_API_LINK, VIDEO_ID_REGEX
from playlist import MasterPlaylist

LINK: Final = "https://rutube.ru/video/a684a67d21eda3792baf1ec433ab653a/"  # 7 минут  # downloaded for ~43 seconds.
# LINK: Final = (
#     "https://rutube.ru/video/940418fbd25740b72410070f540b0cde/"  # 23 минуты
# )
# LINK: Final = (
#     "https://rutube.ru/video/6c58d7354c9a00c9ccfbf7429069ae0b/"  # 41 минуты
# )


async def _get_api_response(
    session: ClientSession, video_id: str
) -> dict[str, Any]:
    try:
        async with session.get(RUTUBE_API_LINK.format(video_id)) as result:
            result.raise_for_status()
            return await result.json()
    except ClientError as e:
        print(f"Error fetching API response: {e}")
        raise ClientError


def extract_video_id(url: str) -> str:
    if result := re.search(VIDEO_ID_REGEX, url):
        return result.group()
    raise ValueError(f"Invalid Rutube URL: {url}")


def extract_title(api_response: dict[str, Any]) -> str:
    video_title = api_response.get("title", "Unknown")
    sanitized_title = re.sub(r"[^\w\-_\. ]", "_", video_title)
    return f"{sanitized_title}.mp4"


async def _download_segment(
    session: ClientSession, segment: m3u8.Segment
) -> bytes:
    try:
        async with session.get(segment.absolute_uri) as response:
            response.raise_for_status()
            return await response.read()
    except ClientError as e:
        print(f"Error downloading segment {segment.absolute_uri}: {e}")
        raise ClientError


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


async def main(link: str) -> None:
    try:
        id = extract_video_id(link)
        async with ClientSession() as session:
            api_response = await _get_api_response(session, id)
            video_title = extract_title(api_response)
            playlist = MasterPlaylist(api_response)
            stream = m3u8.load(playlist.get_best_quality().uri)
            await download_video(stream, session, video_title)
    except Exception as e:
        print(f"Unexpected error during video download: {e}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main(LINK), debug=True)
    end_time = time.time()
    print("download time: ", end_time - start_time)
