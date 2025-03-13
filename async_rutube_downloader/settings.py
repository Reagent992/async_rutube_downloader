import gettext
from typing import Final

from async_rutube_downloader.utils.locale import get_locale, get_resource_path

# Constants
MINUTE: Final = 60
RUTUBE_API_LINK: Final = r"https://rutube.ru/api/play/options/{}/?no_404=true&referer=https%253A%252F%252Frutube.ru&pver=v2"
# regex for video id.
VIDEO_ID_REGEX: Final = r"(?a)(?<=video\/)\w+"
# regex for video url validation
URL_PATTERN: Final = (
    r"(?a)^(https?://rutube\.ru/video/\w+/?)$|^(rutube\.ru/video/\w+/?)$"
)
ID_PATTERN: Final = r"(?a)^\w+$"
URL_FOR_ID_TEMPLATE: Final = "https://rutube.ru/video/{}/"
# Determines how many chunks will be loaded at the same time.
CHUNK_SIZE: Final = 20
FULL_HD_1080p: Final = (1920, 1080)
HD_720p: Final = (1280, 720)

# Application Settings
# Configures log level, while `DEBUG = True` print debug messages.
DEBUG = False

# Locale configuration
domain: Final = "messages"
localedir: Final = "locales"
translation = gettext.translation(
    domain,
    get_resource_path(localedir),
    [get_locale()],
    fallback=True,
)
translation.install()
_ = translation.gettext


# Links to download. Used for testing purposes.
# 1 minutes long
TEST_VIDEO_URL: Final = (
    "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/"
)
TEST_VIDEO_ID: Final = "2ce725b3dc1a243f8456458975ecd872"
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
