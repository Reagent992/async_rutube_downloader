[![release](https://img.shields.io/github/release/Reagent992/async_rutube_downloader.svg)](https://github.com/Reagent992/async_rutube_downloader/releases/latest)
[![tests](https://github.com/Reagent992/async_rutube_downloader/actions/workflows/tests.yml/badge.svg)](https://github.com/Reagent992/async_rutube_downloader/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Reagent992/async_rutube_downloader/badge.svg?branch=main)](https://coveralls.io/github/Reagent992/async_rutube_downloader?branch=main)
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Reagent992/async_rutube_downloader/total?label=release%20downloads)](https://github.com/Reagent992/async_rutube_downloader/releases/latest)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/async_rutube_downloader?label=pypi%20downloads)](https://pypi.org/project/async_rutube_downloader/)



English / [Russian](./README_RU.md)
# What is it?

Small project with one main function - download a video from RuTube(it's a russian copy of YouTube).

## How to use it?

### UI
- Download executable file from [Releases](https://github.com/Reagent992/async_rutube_downloader/releases/latest).

![screen_cast.gif](screen_cast.gif)

### CLI

1. Install library
```
pip install async_rutube_downloader
```
2. Run
```
rtube-cli https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/
```

---

- `rtube-cli --help` output

```
❯ rtube-cli
usage: rtube-cli [-h] [-o] [-q] [-v] [-f] [-d] [url]

This CLI utility allows you to download videos from Rutube.
 - You can download a single video or multiple videos by providing a file with URLs.
 - By default, videos from a file will be downloaded in the best available quality.

positional arguments:
  url                URL or ID of the Rutube video

options:
  -h, --help         show this help message and exit
  -o , --output      Output directory (default: current working directory)
  -q, --quality      Select video quality interactively
  -v, --version      show program's version number and exit

Multiple videos download:
  -f , --file        Path to the file with URLs
  -d , --delimiter   Delimiter between URLs in the file(default: \n)

Usage examples:
 - Download single video:
      [rtube-cli] 365ae8f40a2ffd2a5901ace4db799de7
      [rtube-cli] https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/
      [rtube-cli] https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/ -q
 - Download multiple videos:
      [rtube-cli] -f ~/path/to/file1.txt
      [rtube-cli] -f ~/path/to/file2.txt -d ,
```

### Use in code

1. Install library
```
pip install async_rutube_downloader
```
2. Use example

`qualities` is a tuple, like: `((1280, 720), (1920,1080))`

- async

```python
import asyncio
from async_rutube_downloader.downloader import Downloader


async def download():
    downloader = Downloader(
        "https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/"
    )
    qualities = await downloader.fetch_video_info()
    await downloader.select_quality(max(qualities))
    await downloader.download_video()

asyncio.run(download())
```

- sync

```python
import asyncio
from async_rutube_downloader.downloader import Downloader


loop = asyncio.new_event_loop()
downloader = Downloader(
    "https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/", loop
)
qualities = loop.run_until_complete(downloader.fetch_video_info())
loop.run_until_complete(downloader.select_quality(max(qualities)))
loop.run_until_complete(downloader.download_video())
loop.close()
```

### [Source code](./dev.md)

# About
This project was created for learning purposes and was inspired by a similar synchronous library and a book about async.

## Technical Features
- TKinter UI
- `argparse`(stdlib) CLI
- The honest progress bar shows the actual download progress.
- UI and loading work in different threads.
- UI localization.
- The async version allows you to use the full speed of your internet connection.
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) is used to create an executable file.

## Dependencies

| title                                                           | description                      |
| --------------------------------------------------------------- | -------------------------------- |
| [m3u8](https://github.com/globocom/m3u8/)                       | Used for playlist parsing        |
| [aiohttp](https://github.com/aio-libs/aiohttp)                  | Async http client                |
| [aiofiles](https://github.com/Tinche/aiofiles)                  | async work with files            |
| [slugify ](https://github.com/un33k/python-slugify)             | Convert video title to file name |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Better TKinter UI                |
