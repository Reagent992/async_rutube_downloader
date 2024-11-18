import asyncio
import re
import time
from typing import Any, Final

import m3u8
from aiohttp import ClientSession

from config import RUTUBE_API_LINK, VIDEO_ID_REGEX

LINK: Final = "https://rutube.ru/video/a684a67d21eda3792baf1ec433ab653a/"


async def _get_api_response(session: ClientSession, id: str) -> dict[str, Any]:
    async with session.get(RUTUBE_API_LINK.format(id)) as result:
        result.raise_for_status()
        return await result.json()


async def _get_video_id(url: str) -> str:
    if result := re.search(VIDEO_ID_REGEX, url):
        return result.group()
    else:
        raise ValueError("Wrong url")


def _get_master_playlist(api_response: dict[str, Any]) -> m3u8.M3U8:
    """Retrieve the master m3u8 playlist containing different quality streams."""
    try:
        m3u8_url = api_response["video_balancer"]["m3u8"]
        return m3u8.load(m3u8_url)
    except KeyError:
        raise KeyError("M3U8 playlist URL not found in API response")


def _get_playlist(playlist: m3u8.M3U8) -> m3u8.M3U8:
    return m3u8.load(playlist)


async def _download_segment(
    session: ClientSession, segment: m3u8.Segment
) -> bytes:
    async with session.get(segment.absolute_uri) as response:
        response.raise_for_status()
        return await response.read()


async def main(link: str) -> None:
    id = await _get_video_id(link)
    async with ClientSession() as session:
        api_response = await _get_api_response(session, id)
        video_title = api_response.get("title", "Unknown")
        playlist = _get_master_playlist(api_response)
        # Get the list of quality streams
        streams = playlist.playlists
        # Iterate over the quality streams
        best_stream: m3u8.M3U8 = max(
            streams, key=lambda stream: stream.stream_info.bandwidth
        )
        best_stream = m3u8.load(best_stream.absolute_uri)

        tasks = []
        for segment in best_stream.segments:
            task = asyncio.create_task(
                _download_segment(session, segment),
                name=f"Downloading {segment.absolute_uri}",
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        with open(f"{video_title}.mp4", "wb") as file:
            for result in results:
                file.write(result)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main(LINK), debug=True)
    end_time = time.time()
    print(end_time - start_time)
