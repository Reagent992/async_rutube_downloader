# How to install project locally
1. [Install poetry](https://python-poetry.org/)
2. Copy project `git clone https://github.com/Reagent992/async_rutube_downloader.git`
3. `cd async_rutube_downloader`
4. `poetry install`
5. `poetry run python ./src/run_ui.py`


# Dev notes
- Looks like python installed by **UV** doesn't provide **TKinter** support. So i've switched to **poetry** and **pyenv**.
- build executable command: `poetry run pyinstaller ./src/run_ui.py  --path ./src/ --clean --onefile --noconsole`