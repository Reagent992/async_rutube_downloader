import asyncio
import tomllib
from pathlib import Path
from typing import Literal

from async_rutube_downloader.utils.logger import get_logger

logger = get_logger(__name__)


def get_version_from_pyproject() -> str | Literal["Unknown"]:
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "Unknown")
    logger.error("Unable to find pyproject.toml[used for cli -v flag]")
    return "Unknown"


def resolve_file_name(directory: Path, file_name: str, format: str) -> Path:
    counter = 0
    while True:
        if not counter:
            new_file_name = f"{file_name}.{format}"
        else:
            new_file_name = f"{file_name}({counter}).{format}"
        new_file = directory / Path(new_file_name)
        if new_file.exists():
            counter += 1
            logger.info("File %s exists, trying next name", new_file_name)
            continue
        else:
            return new_file


def get_or_create_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
