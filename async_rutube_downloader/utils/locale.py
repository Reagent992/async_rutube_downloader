import locale
import os
import sys
from pathlib import Path


def get_locale() -> str:
    if lang := os.environ.get("LANG"):
        return "ru" if lang.startswith("ru") else "en"

    system_locale, _ = locale.getdefaultlocale()
    try:
        lang = system_locale.split("_")[0] if system_locale else "en"
    except IndexError:
        lang = "en"
    return lang


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource for both
    development and PyInstaller bundle"""
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = getattr(sys, "_MEIPASS", Path.cwd())
    return str(Path(base_path) / relative_path)
