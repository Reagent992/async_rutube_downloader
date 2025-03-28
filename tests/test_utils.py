import m3u8

from async_rutube_downloader.utils.type_hints import (
    Qualities,
    QualitiesWithPlaylist,
)


def is_valid_qualities(qualities: Qualities) -> bool:
    """
    Validate the qualities dictionary.
    Qualities should be tuple[tuple[int, int], ...]
    """
    if not isinstance(qualities, tuple):
        return False
    for width, high in qualities:
        if not (isinstance(width, int) and isinstance(high, int)):
            return False
    return True


def is_valid_qualities_with_playlist(qualities: QualitiesWithPlaylist) -> bool:
    """
    Validate the qualities dictionary.
    Qualities should be dict[tuple[int, int], m3u8.Playlist]
    """
    if not isinstance(qualities, dict):
        return False
    for key, value in qualities.items():
        if not (
            isinstance(key, tuple)
            and len(key) == 2
            and all(isinstance(i, int) for i in key)
        ):
            return False
        if not isinstance(value, m3u8.Playlist):
            return False
    return True
