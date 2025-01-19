from typing import Self

import m3u8
from aiohttp import ClientSession

from utils.decorators import retry
from utils.exceptions import MasterPlaylistInitializationError
from utils.type_hints import Qualities


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
        self.qualities: Qualities | None = None

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
            # TODO: Should i pass uri in loads here?
            return m3u8.loads(await response.text())

    def __get_qualities(self) -> Qualities:
        if not self._master_playlist:
            raise MasterPlaylistInitializationError(
                "Master playlist not loaded. Call run() method first."
            )
        qualities: Qualities = {}
        for playlist in self._master_playlist.playlists:
            resolution = playlist.stream_info.resolution
            if resolution and resolution not in qualities:
                qualities[resolution] = playlist
            # TODO: There are 2 CDNs in the master playlist,
            #  we can potentially use the second one for retry.
            # but now just skip it.
        return qualities
