from typing import Any

import m3u8

type Qualities = dict[tuple[int, int], m3u8.Playlist]
type APIResponseDict = dict[str, Any]
