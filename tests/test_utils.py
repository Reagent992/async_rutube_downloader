import m3u8


def validate_qualities(qualities) -> bool:
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
