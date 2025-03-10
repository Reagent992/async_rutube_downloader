import locale
import os
import sys


def get_locale() -> str:
    if lang := os.environ.get("LANG"):
        return "ru" if lang.startswith("ru") else "en"

    system_locale, _ = locale.getdefaultlocale()
    try:
        lang = system_locale.split("_")[0] if system_locale else "en"
    except IndexError:
        lang = "en"
    return lang


def get_resource_path(relative_path) -> str:
    """Get absolute path to resource for both
    development and PyInstaller bundle"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS  # type: ignore
        else:
            raise AttributeError
    except (AttributeError, Exception):
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
