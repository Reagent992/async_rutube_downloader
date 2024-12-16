from typing import Optional, Self, TypeAlias

import m3u8
from aiohttp import ClientSession

Qualities: TypeAlias = dict[tuple[int, int], m3u8.Playlist]


class MasterPlaylist:
    """
    Used to parse a Master M3U8 playlist into multiple playlists,
    each corresponding to a different quality level.

    Methods:
        run(): Makes an API call to retrieve information.
    """

    def __init__(
        self,
        link_to_master_playlist: str,
        session: ClientSession,
    ) -> None:
        """
        Args:
            link_to_master_playlist (str): The URL of the master playlist
            session (ClientSession): The aiohttp session to use
                for http the request.
        """
        self._link_to_master_playlist = link_to_master_playlist
        self._session = session
        self._master_playlist: Optional[m3u8.M3U8] = None
        self.qualities: Optional[Qualities] = None

    async def _get_master_playlist(self) -> None:
        response = await self._session.get(self._link_to_master_playlist)
        self._master_playlist = m3u8.loads(await response.text())

    async def run(self) -> Self:
        """
        1. Create object like: MasterPlaylist(api_response, session)
        2. Call async run() method to make http requests.
        3. Now you can select video quality.
        """
        await self._get_master_playlist()
        self.qualities = self._get_qualities()
        return self

    def _get_qualities(self) -> Qualities:
        if not self._master_playlist:
            raise AttributeError(
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
