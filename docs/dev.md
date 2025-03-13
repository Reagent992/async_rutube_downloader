# How to install project locally
1. [Install poetry](https://python-poetry.org/) use another package manager that supports **pyproject.toml** (read about **uv** lower)
2. Copy project `git clone https://github.com/Reagent992/async_rutube_downloader.git`
3. `cd async_rutube_downloader`
4. `poetry install` or `poetry install --extras dev` to install all dev dependencies
5. `poetry run python ./async_rutube_downloader/run_ui.py` or just `run_ui`


# Dev notes
- Looks like python installed by **UV** doesn't provide **TKinter** support. So i've switched to **poetry** and **pyenv**.
- build executable command: `poetry run pyinstaller ./async_rutube_downloader/run_ui.py  --path ./async_rutube_downloader/ --clean --onefile --noconsole` or just `make build`



## TODO

- [x] Make a download stable.
- [x] basic refactoring.
- [x] test speed with processing. no improvements.
- [x] Update Downloader to work with UI.
- [x] UI by Tkinter. To make a responsive UI - Tkinter should be in main thread, when asyncio event loop should be in separate thread.
- [x] Check m3u8 didn't make sync connections. [link](https://github.com/globocom/m3u8/wiki/FAQ#how-to-use-a-custom-python-http-client)
looks like we need swap `load()` with `loads(m3u8: str)` and download m3u8 async by aiohttp.
- [x] timeouts for download.
- [x] Use only one `ClientSession` in `Downloader`.
- [x] fix "invalid url" with http://
- [x] long video title breaks UI
- [x] printable video title and safe-file-name title must be different
- [x] fix "Unclosed connector"
- [x] tests
- [x] Make the UI less ugly.
- [x] add threading to UI
- [x] russian ui.
- [x] build ci
- [x] run tests ci
- [ ] add video thumbnail in UI
- [ ] cli client("in process" and quality choose.).
- [ ] Mass download support.
- [ ] Cancel download (method and button for ui)
- [ ] continue download
- [ ] pypi library.
- [ ] shorts support
