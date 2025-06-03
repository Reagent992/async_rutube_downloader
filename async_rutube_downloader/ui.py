import asyncio
import tkinter
from asyncio import AbstractEventLoop, new_event_loop
from concurrent.futures import Future
from enum import Enum, auto
from pathlib import Path
from queue import Queue
from tkinter import filedialog, messagebox
from typing import Final

import customtkinter as ctk

from async_rutube_downloader.settings import DOWNLOAD_CANCELED, _
from async_rutube_downloader.utils.create_session import create_aiohttp_session
from async_rutube_downloader.utils.exceptions import (
    APIResponseError,
    DownloaderIsNotInitializerError,
    FolderDoesNotExistError,
    InvalidURLError,
    M3U8URLNotFoundError,
    MasterPlaylistInitializationError,
    QualityError,
    SegmentDownloadError,
    UploadDirectoryNotSelectedError,
)
from async_rutube_downloader.utils.interfaces import DownloaderABC

INVALID_URL_MSG: Final[str] = _(
    "The provided URL is invalid. Please check and try again."
)
API_RESPONSE_ERROR_MSG: Final[str] = _(
    "Failed to fetch video data. "
    "The URL might be incorrect, or there may be a connection issue."
)
SEGMENT_DOWNLOAD_ERROR_MSG: Final[str] = _(
    "A network issue occurred while downloading a video "
    "segment. Please check your internet connection and retry."
)
ERROR_COLOR: Final[str] = "red"
DOWNLOAD: Final[str] = _("Download")
CANCEL_DOWNLOAD: Final[str] = _("Cancel download")


class State(Enum):
    cancel = auto()
    disable = auto()
    normal = auto()


class DownloaderUI(ctk.CTk):
    """
    UI for Rutube Downloader created with CustomTKinter.
    """

    def __init__(
        self,
        downloader_class: type[DownloaderABC],
        loop: AbstractEventLoop = new_event_loop(),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._downloader_type = downloader_class
        self._loop = loop
        self._session = create_aiohttp_session(self._loop)
        self._refresh_ms = 25
        self._queue: Queue = Queue()
        self._download: DownloaderABC | None = None
        self._upload_directory: Path | None = None
        self.__error_counter: str = ""

        # Configure window
        self.title(_("Rutube Downloader"))
        self.geometry("750x250")
        self.TEXT_WRAP_LENGTH = 450
        # Column "0" will be extended to full width.
        self.grid_columnconfigure(0, weight=1)

        # Select folder
        self._folder_button = ctk.CTkButton(
            self, text=_("Select Folder"), command=self.select_folder
        )
        self._folder_button.grid(column=1, row=0, padx=10, pady=15)
        self._chosen_directory = ctk.CTkLabel(
            self,
            text=_("No folder selected"),
            wraplength=self.TEXT_WRAP_LENGTH,
        )
        self._chosen_directory.grid(column=0, row=0, padx=10, pady=15)

        # URL input
        self._url_entry = ctk.CTkEntry(
            self, width=300, placeholder_text=_("Enter RuTube URL or Video ID")
        )
        self._url_entry.bind("<Return>", self.fetch_video_info)
        self._url_entry.grid(column=0, row=1, padx=10, pady=10, sticky="ew")

        # Get video info
        self._fetch_result_label = ctk.CTkLabel(self, text="")
        self._fetch_result_label.grid(column=0, row=2, padx=10, pady=10)
        # Get video info button
        self._video_info_button = ctk.CTkButton(
            self,
            text=_("Get Video Info"),
            command=self.fetch_video_info,
            state=tkinter.DISABLED,
        )
        self._video_info_button.grid(column=1, row=1, padx=10, pady=10)

        # Video title
        self._video_title_dynamic = ctk.CTkLabel(
            self, text="", wraplength=self.TEXT_WRAP_LENGTH
        )
        self._video_title_dynamic.grid(column=0, row=2, padx=10, pady=10)

        # Dropdown for qualities
        self._dropdown = ctk.CTkComboBox(self, state=tkinter.DISABLED)
        self._dropdown.grid(column=0, row=3, padx=10, pady=10)

        # Download button
        self._download_button = ctk.CTkButton(
            self,
            text=_("Download"),
            command=self.start_download,
            state=tkinter.DISABLED,
        )
        self._download_button.grid(column=1, row=3, padx=10, pady=10)

        # Progress bar
        self._progress_bar = ctk.CTkProgressBar(self)
        self._progress_bar.grid(
            column=0, columnspan=2, row=4, padx=10, pady=10, sticky="ew"
        )
        self._progress_bar.set(0)
        # Customtkinter progress bar have 0-1 range, so we need to divide it
        self._progress_bar_divider = 100

    def _update_bar(self, progress_bar_value: int) -> None:
        """Update the progress bar.
        Call only from main thread."""
        if progress_bar_value == 100 and self._download:
            messagebox.showinfo(
                _("Download Complete"),
                _("Download Complete"),
            )
            #  TODO: A "Download Complete" alert is shown
            # a little bit before the last downloaded chunk is actually saved.
            self._download = None
            self._progress_bar.set(1)
            self.change_download_button_state(State.normal)
        else:
            self._progress_bar.set(
                progress_bar_value / self._progress_bar_divider
            )
            self.after(self._refresh_ms, self._poll_queue)

    def _queue_update(
        self, completed_requests: int, total_requests: int
    ) -> None:
        """Callback func passed to Downloader.
        Used to put progress bar update in the queue."""
        self._queue.put(int((completed_requests / total_requests) * 100))

    def _poll_queue(self) -> None:
        """Constantly check the queue for a progress bar update."""
        if not self._queue.empty():
            percent_complete = self._queue.get()
            self._update_bar(percent_complete)
        else:
            if self._download:
                self.after(self._refresh_ms, self._poll_queue)

    def fetch_video_info(self, *args) -> None:
        """
        1. Fetch video info from Rutube API.
        2. Fill the UI with fetched info or display an error message.

        Args:
            *args: Press **Enter** in the URL input area, creates an object,
                this object goes here.
        """
        self._fetch_result_label.configure(text="")
        self.change_download_button_state(State.normal)
        if not self._url_entry.get():
            messagebox.showerror(
                _("Error"),
                _("Please enter a video URL before proceeding."),
            )
        elif self._upload_directory and self._url_entry.get():
            self._fetch_video_info()

    def __increase_error_counter(self) -> None:
        if self.__error_counter:
            self.__error_counter = str(int(self.__error_counter) + 1)
        else:
            self.__error_counter = "1"

    def _fetch_video_info(self) -> None:
        """
        1. Creates a Downloader object in the main thread.
        2. Executes its `fetch_video_info` method in a separate thread,
        where an event loop is running.
        """
        try:
            if not self._upload_directory:
                raise UploadDirectoryNotSelectedError
            self._download = self._downloader_type(
                self._url_entry.get(),
                self._loop,
                self._queue_update,
                self._upload_directory,
                self._session,
                auto_close_session=False,
            )
            download_future = asyncio.run_coroutine_threadsafe(
                self._download.fetch_video_info(), self._loop
            )
            download_future.add_done_callback(self._on_video_info_fetched)
        except (InvalidURLError, M3U8URLNotFoundError):
            self._fetch_result_label.configure(
                text=INVALID_URL_MSG + self.__error_counter,
                text_color=ERROR_COLOR,
            )
            self.__increase_error_counter()

    def _on_video_info_fetched(self, download_future: Future) -> None:
        try:
            self._download_available_qualities = download_future.result()
            self._update_ui_with_video_info()
        except (APIResponseError, MasterPlaylistInitializationError):
            self._fetch_result_label.configure(
                text=API_RESPONSE_ERROR_MSG + self.__error_counter,
                text_color=ERROR_COLOR,
            )
            self.__increase_error_counter()
        except SegmentDownloadError:
            self._fetch_result_label.configure(
                text=SEGMENT_DOWNLOAD_ERROR_MSG + self.__error_counter,
                text_color=ERROR_COLOR,
            )
            self.__increase_error_counter()

    def _update_ui_with_video_info(self):
        self.__fill_qualities()
        self.__fill_title()

    def __fill_qualities(self) -> None:
        fields = [f"{x}x{y}" for x, y in self._download_available_qualities]
        self._dropdown.configure(values=fields, state=tkinter.NORMAL)
        self._dropdown.set(fields[-1])

    def __fill_title(self) -> None:
        if self._download:
            self._video_title_dynamic.configure(
                text=self._download.video_title
            )

    def start_download(self) -> None:
        """Download the video from the given URL."""
        if self._download:
            self.__set_quality()
            asyncio.run_coroutine_threadsafe(
                self._download.download_video(), self._loop
            )
            self.change_download_button_state(State.cancel)
            self.after(self._refresh_ms, self._poll_queue)

    def change_download_button_state(self, state: State) -> None:
        states = {
            State.cancel: {
                "text": CANCEL_DOWNLOAD,
                "command": self.cancel_download,
                "state": tkinter.NORMAL,
            },
            State.disable: {
                "text": DOWNLOAD,
                "command": None,
                "state": tkinter.DISABLED,
            },
            State.normal: {
                "text": DOWNLOAD,
                "command": self.start_download,
                "state": tkinter.NORMAL,
            },
        }
        self._download_button.configure(**states[state])

    def cancel_download(self) -> None:
        assert self._download
        self._download.interrupt_download()
        messagebox.showinfo(_("Info"), DOWNLOAD_CANCELED)
        self.change_download_button_state(State.disable)
        self.clean_ui()

    def clean_ui(self) -> None:
        """Clean up: title, qualities,progress,bar"""
        self._video_title_dynamic.configure(text="")
        self._progress_bar.set(0)
        self._dropdown.configure(values=[], state=tkinter.DISABLED)
        self._dropdown.set("")

    def __set_quality(self) -> None:
        """
        Set the quality of the video to download.
        """
        if self._download is None:
            raise DownloaderIsNotInitializerError
        selected_quality = self.__get_selected_quality()
        quality_future = asyncio.run_coroutine_threadsafe(
            self._download.select_quality(selected_quality), self._loop
        )
        quality_future.result()

    def __get_selected_quality(self) -> tuple[int, int]:
        quality = tuple(map(int, self._dropdown.get().split("x")))
        if len(quality) == 2:
            return quality
        raise QualityError

    def select_folder(self) -> None:
        directory = filedialog.askdirectory(title="Select Download Folder")
        if directory:
            self._chosen_directory.configure(text=directory)
            self._upload_directory = Path(directory)
            if not self._upload_directory.is_dir():
                raise FolderDoesNotExistError
            self._video_info_button.configure(state="normal")
