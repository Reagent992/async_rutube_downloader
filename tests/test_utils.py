from async_rutube_downloader.utils.type_hints import Qualities


def validate_qualities(qualities: Qualities) -> bool:
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
