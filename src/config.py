# RuTube api link.
RUTUBE_API_LINK = r"https://rutube.ru/api/play/options/{}/?no_404=true&referer=https%253A%252F%252Frutube.ru&pver=v2"

# regex for video id.
VIDEO_ID_REGEX = r"(?a)(?<=video\/)[\w\d]+"

# regex for video url validation
URL_PATTERN = (
    r"(?a)^(https://rutube\.ru/video/[\w\d]+/)|(rutube\.ru/video/[\w\d]+/?)$"
)
ID_PATTERN = r"(?a)^[\w\d]+$"
URL_FOR_ID_TEMPLATE = "https://rutube.ru/video/{}/"

# Determines how many chunks will be loaded at the same time.
CHUNK_SIZE = 20


# Links to download. Used for testing purposes.
# 1 minutes long
LINK = "https://rutube.ru/video/2ce725b3dc1a243f8456458975ecd872/"
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
