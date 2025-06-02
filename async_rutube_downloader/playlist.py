from typing import Self

import m3u8
from aiohttp import ClientSession

from async_rutube_downloader.utils.decorators import retry
from async_rutube_downloader.utils.exceptions import (
    APIResponseError,
    MasterPlaylistInitializationError,
)
from async_rutube_downloader.utils.logger import get_logger
from async_rutube_downloader.utils.type_hints import QualitiesWithPlaylist

logger = get_logger(__name__)


class MasterPlaylist:
    """
    Used to parse a Master M3U8 playlist into multiple playlists,
    each corresponding to a different quality level.

    Methods:
        run(): Makes an API call to retrieve information.
    """

    def __init__(
        self,
        master_playlist_url: str,
        session: ClientSession,
    ) -> None:
        """
        Args:
            master_playlist_url (str): The URL of the master playlist
            session (ClientSession): The aiohttp session to use
                for http the request.
        """
        self._master_playlist_url = master_playlist_url
        self._session = session
        self._master_playlist: m3u8.M3U8 | None = None
        self.qualities: QualitiesWithPlaylist | None = None

    async def run(self) -> Self:
        """
        1. Create object like: `MasterPlaylist(api_response, session)`
        2. Call async `run()` method to make http requests.
        3. Now you can select video quality from `self.qualities` attribute.
        """
        self._master_playlist = await self.__get_master_playlist()
        self.qualities = self.__get_qualities()
        return self

    @retry(
        "Failed to download master playlist", MasterPlaylistInitializationError
    )
    async def __get_master_playlist(self) -> m3u8.M3U8:
        async with self._session.get(self._master_playlist_url) as response:
            try:
                return m3u8.loads(
                    await response.text(), self._master_playlist_url
                )
            except Exception as e:
                logger.info(
                    "An error occurred while parsing the Master Playlist",
                    exc_info=True,
                )
                raise APIResponseError(str(e))

    def __get_qualities(self) -> QualitiesWithPlaylist:
        if not self._master_playlist:
            raise MasterPlaylistInitializationError
        qualities: QualitiesWithPlaylist = {}
        for playlist in self._master_playlist.playlists:
            resolution = playlist.stream_info.resolution
            if resolution and resolution not in qualities:
                qualities[resolution] = playlist
            # TODO: There are 2 CDNs in the master playlist,
            # we can potentially use the second one for retry.
            # but now just skip it.
        return qualities
