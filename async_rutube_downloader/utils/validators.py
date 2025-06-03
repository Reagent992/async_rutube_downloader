from pathlib import Path

from async_rutube_downloader.utils.exceptions import OutputDirectoryError


def cli_quality_validator(
    user_input: str | None, qualities: dict[int, tuple[int, int]]
) -> bool:
    """
    CLI output qualities:
    1. 432x232
    2. 640x360

    User input: 1

    This function ensures the input is a number and exists
    in the available options.
    """

    if not user_input:
        return False
    if not user_input.isnumeric():
        return False
    selected_quality_index = int(user_input)
    if selected_quality_index in qualities:
        return True
    return False


def cli_validate_urls_file(urls: list[str]) -> bool:
    if not urls:
        return False
    if not any(bool(url) for url in urls):
        return False
    return True


def cli_validate_path(output: str) -> Path:
    path = Path(output)
    if not path.exists():
        raise OutputDirectoryError(output)
    return path


def is_quality_valid(selected_quality: tuple[int, int]) -> bool:
    if (
        isinstance(selected_quality, tuple)
        and len(selected_quality) == 2
        and all(isinstance(i, int) and i > 0 for i in selected_quality)
    ):
        return True
    return False
