# How to install project locally
1. [Install poetry](https://python-poetry.org/) or use another package manager that supports **pyproject.toml** (read about **uv** lower)
2. Copy project `git clone https://github.com/Reagent992/async_rutube_downloader.git`
3. `cd async_rutube_downloader`
4. `poetry install` or `poetry install --extras dev` to install all developer dependencies
5. `poetry run python ./async_rutube_downloader/run_ui.py` or just `run_ui`

## How in add a dependency(poetry)
When dev dependencies are in `[project.optional-dependencies]`, you can use a different project manager.
1. `poetry add pre-commit --optional=dev`
2. `poetry install --extras dev`

# Dev notes
- Looks like python installed by **UV** doesn't provide **TKinter** support. So i've switched to **poetry** and **pyenv**.
- build executable command: `poetry run pyinstaller ./async_rutube_downloader/run_ui.py  --path ./async_rutube_downloader/ --clean --onefile --noconsole` or just `make build`
- **GNU gettext** doesn't work with **f-strings**, use `_('Hey {},').format(username)` instead
- `pre-commit install` to activate git hooks



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
- [x] cli client("in process" and quality choose.).
- [x] Mass download support[CLI].
- [x] Cancel download[CLI] (method and button for ui)
- [x] Cancel download[UI]
- [x] tests for cli client
- [x] pypi library.
- [ ] add video thumbnail in UI
- [ ] continue download
- [ ] shorts/etc. support
