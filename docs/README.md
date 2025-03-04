[![release](https://img.shields.io/github/release/Reagent992/async_rutube_downloader.svg)](https://github.com/Reagent992/async_rutube_downloader/releases/latest)

English / [Russian](./README_RU.md)
# What is it?

Small project with one main function - download a video from RuTube(it's a russian copy of YouTube).

## How to use it?

- Simple way: Download executable file from [Releases](https://github.com/Reagent992/async_rutube_downloader/releases/latest).
- Hard way: [install project](./dev.md)

![screen_cast](screen_cast.gif)

# About
- This project was created for learning purposes and was inspired by a similar synchronous library and a book about async.
- The async version allows you to use the full speed of your internet connection.

## Technical Features
- Progress bar displays the real download progress.
- UI and loading work in different threads.
- UI localization.

# Used libs

| title                                                           | description                      |
| --------------------------------------------------------------- | -------------------------------- |
| [m3u8](https://github.com/globocom/m3u8/)                       | Used for playlist parsing        |
| [aiohttp](https://github.com/aio-libs/aiohttp)                  | Async http client                |
| [aiofiles](https://github.com/Tinche/aiofiles)                  | async work with files            |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller)       | Create executable files          |
| [slugify ](https://github.com/un33k/python-slugify)             | Convert video title to file name |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Better TKinter UI                |
