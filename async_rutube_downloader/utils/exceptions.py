from argparse import ArgumentTypeError


class OutputDirectoryError(ArgumentTypeError):
    def __init__(self, output: str) -> None:
        super().__init__(f"Directory '{output}' does not exist.")


class RuTubeDownloaderError(Exception):
    """Base class for all errors raised by the downloader."""


class InvalidURLError(RuTubeDownloaderError):
    """Wrong RuTube URL passed. So there is nothing to download."""

    def __init__(self, url: str | None = None) -> None:
        super().__init__(f"Invalid Rutube URL: {url}")


class APIResponseError(RuTubeDownloaderError):
    def __init__(self, error_text: str | None = None) -> None:
        super().__init__(
            f"An error occurred while parsing the Master Playlist {error_text}"
        )


class InvalidPlaylistError(RuTubeDownloaderError):
    def __init__(self) -> None:
        super().__init__("Invalid playlist selected")


class SegmentDownloadError(RuTubeDownloaderError): ...


class MasterPlaylistInitializationError(RuTubeDownloaderError):
    def __init__(self) -> None:
        super().__init__(
            "Master playlist is not initialized, call run() method first"
        )


class QualityError(RuTubeDownloaderError):
    def __init__(self) -> None:
        super().__init__("Quality must be a tuple of two integers")


class M3U8URLNotFoundError(KeyError):
    def __init__(self) -> None:
        super().__init__("M3U8 playlist URL not found in API response.")


class UIRutubeDownloaderError(Exception):
    """Base class for all errors raised by the UI."""


class UploadDirectoryNotSelectedError(UIRutubeDownloaderError):
    """You must select folder at first."""


class DownloaderIsNotInitializerError(UIRutubeDownloaderError):
    def __init__(self) -> None:
        super().__init__("You must initialize Downloader object first.")


class FolderDoesNotExistError(UIRutubeDownloaderError):
    def __init__(self) -> None:
        super().__init__("Selected folder does not exist")


class CLIRutubeDownloaderError(Exception):
    """Base class for all errors raised by the CLI."""


class CLIFileError(CLIRutubeDownloaderError): ...
