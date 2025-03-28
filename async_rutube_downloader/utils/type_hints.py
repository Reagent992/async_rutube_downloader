from typing import Any

import m3u8

type QualitiesWithPlaylist = dict[tuple[int, int], m3u8.Playlist]
type Qualities = tuple[tuple[int, int], ...]
type APIResponseDict = dict[str, Any]
