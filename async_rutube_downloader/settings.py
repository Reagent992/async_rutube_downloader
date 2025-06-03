import gettext
from typing import Final

from async_rutube_downloader.utils.locale import get_locale, get_resource_path

########################################################## Application Settings
# Configures log level, while `DEBUG = True` print debug messages.
DEBUG: Final[bool] = False
# Locale configuration
domain: Final[str] = "messages"
localedir: Final[str] = "locales"
translation = gettext.translation(
    domain,
    get_resource_path(localedir),
    [get_locale()],
    fallback=True,
)
translation.install()
_ = translation.gettext
##################################################################### Constants
MINUTE: Final[int] = 60
RUTUBE_API_LINK: Final[str] = (
    r"https://rutube.ru/api/play/options/{}/?no_404=true&referer=https%253A%252F%252Frutube.ru&pver=v2"
)
VIDEO_FORMAT: Final[str] = "mp4"
# regex for video id.
VIDEO_ID_REGEX: Final[str] = r"(?a)(?<=video\/)\w+"
# regex for video url validation
URL_PATTERN: Final[str] = (
    r"(?a)^(https?://rutube\.ru/video/\w+/?)$|^(rutube\.ru/video/\w+/?)$"
)
ID_PATTERN: Final[str] = r"(?a)^\w+$"
URL_FOR_ID_TEMPLATE: Final[str] = "https://rutube.ru/video/{}/"
# Determines how many chunks will be loaded at the same time.
CHUNK_SIZE: Final[int] = 20
FULL_HD_1080p: Final[tuple[int, int]] = (1920, 1080)
HD_720p: Final[tuple[int, int]] = (1280, 720)
# CLI_TEXT
CLI_NAME: Final[str] = "rtube-cli"
CLI_DESCRIPTION: Final[str] = _("""
This CLI utility allows you to download videos from Rutube.
 - You can download a single video or multiple videos by providing a file with\
 URLs.
 - By default, videos from a file will be downloaded in the best available\
 quality.
""")
CLI_EPILOG: Final[str] = _(
    """
Usage examples:
 - Download single video:
      [{cli_name}] 365ae8f40a2ffd2a5901ace4db799de7
      [{cli_name}]\
 https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/
      [{cli_name}]\
 https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/ -q
 - Download multiple videos:
      [{cli_name}] -f ~/path/to/file1.txt
      [{cli_name}] -f ~/path/to/file2.txt -d ,
"""
).format(cli_name=CLI_NAME)
API_RESPONSE_ERROR_MSG: Final[str] = _(
    "Resource not found (404) "
    "The URL may be incorrect, or the API might be unavailable."
)
INVALID_URL: Final[str] = _("Invalid URL")
INVALID_FILE_ERROR_MSG: Final[str] = _(
    "Invalid file. The file contains errors "
    "or does not meet validation requirements."
)
FILE_NOT_FOUND_ERROR_MSG: Final[str] = _("No such file or directory: {}")
PATH_IS_A_DIRECTORY_ERROR_MSG: Final[str] = _(
    "The given path is a directory: {}"
)
REPORT_MULTIPLE_URLS: Final[str] = _(
    "Report: Downloaded {} videos, "
    "Invalid urls {}, it takes {} minutes, {} seconds"
)
DOWNLOAD_DIR: Final[str] = _("Download directory: {}")
DOWNLOAD_CANCELED: Final[str] = _("Download cancelled")
AVAILABLE_QUALITIES: Final[str] = _("Available qualities:")
SELECT_QUALITY: Final[str] = _(
    "Select quality. (Enter the corresponding number)"
)
##################################################################### TEST_INFO
# Links to download. Used for testing purposes.
# 1 minute long
TEST_VIDEO_URL: Final[str] = (
    "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/"
)
TEST_VIDEO_ID: Final[str] = "2ce725b3dc1a243f8456458975ecd872"
# LINK = "2ce725b3dc1a243f8456458975ecd872"  # same, but only id
# downloaded for ~7 seconds

# 7 minutes long
# LINK = "https://rutube.ru/video/a684a67d21eda3792baf1ec433ab653a/"
# downloaded for ~35 seconds seconds with 50 chunk size and aiofiles
# downloaded for ~40 seconds seconds with 50 chunk size and processes

# 23 minutes long
# LINK = "https://rutube.ru/video/940418fbd25740b72410070f540b0cde/"
# downloaded for ~101 seconds with 50 chunk size and aiofiles
# downloaded for ~116 seconds with 50 chunk size and processes

# 41 minutes long
# LINK = "https://rutube.ru/video/6c58d7354c9a00c9ccfbf7429069ae0b/"
