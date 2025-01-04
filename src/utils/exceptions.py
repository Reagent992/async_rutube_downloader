class RuTubeDownloaderError(Exception):
    """Base class for all errors raised by the downloader."""


class InvalidURLError(RuTubeDownloaderError):
    """Wrong RuTube URL passed. So there is nothing to download."""


class APIResponseError(RuTubeDownloaderError): ...


class InvalidPlaylistError(RuTubeDownloaderError): ...


class SegmentDownloadError(RuTubeDownloaderError): ...


class MasterPlaylistInitializationError(RuTubeDownloaderError):
    """Exception for rare situation when MasterPlaylist object is created
    but, run method is not called."""


class QualityError(RuTubeDownloaderError): ...


class UIRutubeDownloaderError(Exception):
    """Base class for all errors raised by the UI."""


class UploadDirectoryNotSelectedError(UIRutubeDownloaderError):
    """You must select folder at first."""


class DownloaderIsNotInitializerError(UIRutubeDownloaderError):
    """You mist initialize Downloader object first."""
