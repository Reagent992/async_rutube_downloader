import asyncio
import re
import time
from typing import Any, Final

import aiofiles
import m3u8
from aiohttp import ClientSession

from config import CHUNK_SIZE, RUTUBE_API_LINK, VIDEO_ID_REGEX
from playlist import MasterPlaylist

LINK: Final = (
    "https://rutube.ru/video/a684a67d21eda3792baf1ec433ab653a/"  # 7 минут
)
# LINK: Final = (
#     "https://rutube.ru/video/940418fbd25740b72410070f540b0cde/"  # 23 минуты
# )
# LINK: Final = (
#     "https://rutube.ru/video/6c58d7354c9a00c9ccfbf7429069ae0b/"  # 41 минуты
# )


async def _get_api_response(session: ClientSession, id: str) -> dict[str, Any]:
    async with session.get(RUTUBE_API_LINK.format(id)) as result:
        result.raise_for_status()
        return await result.json()


def _get_video_id(url: str) -> str:
    if result := re.search(VIDEO_ID_REGEX, url):
        return result.group()
    else:
        raise ValueError("Wrong url")


async def _download_segment(
    session: ClientSession, segment: m3u8.Segment
) -> bytes:
    async with session.get(segment.absolute_uri) as response:
        response.raise_for_status()
        return await response.read()


async def write_to_file(segment_data: bytes, file_name: str) -> None:
    async with aiofiles.open(file_name, mode="ab") as file:
        await file.write(segment_data)


async def download(
    stream: m3u8.M3U8, session: ClientSession, video_title: str
) -> None:
    segments = list(stream.segments)
    file_name = f"{video_title}.mp4"

    # Process segments in chunks
    for i in range(0, len(segments), CHUNK_SIZE):
        tasks = []
        for segment in segments[i : i + CHUNK_SIZE]:
            task = asyncio.create_task(_download_segment(session, segment))
            tasks.append(task)

        downloaded_segments = await asyncio.gather(*tasks)

        # Write downloaded segments asynchronously
        write_tasks = [
            asyncio.create_task(write_to_file(data, file_name))
            for data in downloaded_segments
        ]
        await asyncio.gather(*write_tasks)


async def main(link: str) -> None:
    id = _get_video_id(link)
    async with ClientSession() as session:
        api_response = await _get_api_response(session, id)
        video_title = api_response.get("title", "Unknown")
        playlist = MasterPlaylist(api_response)
        stream = m3u8.load(playlist.get_best_quality().uri)
        await download(stream, session, video_title)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main(LINK), debug=True)
    end_time = time.time()
    print("download time: ", end_time - start_time)
