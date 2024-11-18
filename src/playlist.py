from typing import Any, TypeAlias

import m3u8

Qualities: TypeAlias = dict[str, list[m3u8.M3U8]]


class MasterPlaylist:
    def __init__(self, data: dict[str, Any]) -> None:
        self.master_playlist = data
        self.qualities = self._get_qualities()

    @property
    def master_playlist(self) -> m3u8.M3U8:
        return self.__master_playlist

    @master_playlist.setter
    def master_playlist(self, data: dict[str, Any]) -> m3u8.M3U8:
        """Retrieve the master m3u8 playlist
        containing different quality streams."""
        try:
            master_playlist_url = data["video_balancer"]["m3u8"]
            self.__master_playlist = m3u8.load(master_playlist_url)
        except KeyError:
            raise KeyError("M3U8 playlist URL not found in API response")

    def _get_qualities(self) -> Qualities:
        qualities: Qualities = {}
        for playlist in self.__master_playlist.playlists:
            resolution = playlist.stream_info.resolution
            if resolution not in qualities:
                qualities[resolution] = []
            qualities[resolution].append(playlist)
        return qualities

    def get_best_quality(self) -> m3u8.M3U8:
        # FIXME: There is 2 cdn. Used the first one.
        return self.qualities[max(self.qualities)].pop()


# class RegularPlaylist:
#     def __init__(self, data: m3u8.M3U8) -> None:
#         self.__playlist = data

#     @property
#     def playlist(self) -> m3u8.M3U8:
#         return self.__playlist

#     @playlist.setter
#     def playlist(self, data: m3u8.M3U8) -> m3u8.M3U8:
#         self.__playlist = m3u8.load(data)
