import asyncio
from asyncio import AbstractEventLoop, new_event_loop
from pathlib import Path
from queue import Queue
from tkinter import filedialog, messagebox

import customtkinter as ctk

from downloader import Downloader
from utils.create_session import create_aiohttp_session
from utils.exceptions import (
    APIResponseError,
    DownloaderIsNotInitializerError,
    InvalidURLError,
    MasterPlaylistInitializationError,
    UploadDirectoryNotSelectedError,
)


class DownloaderUI(ctk.CTk):
    """
    UI for Rutube Downloader created with customtkinter.
    """

    def __init__(
        self, loop: AbstractEventLoop = new_event_loop(), *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        ctk.set_appearance_mode("dark")  # Light/ Dark / System
        ctk.set_default_color_theme("blue")  # blue / dark-blue / green

        self._loop = loop
        self._session = create_aiohttp_session(self._loop)
        self._refresh_ms = 25
        self._queue: Queue = Queue()
        self._download: Downloader | None = None
        self._upload_directory: Path | None = None

        self.title("Rutube Downloader")
        self.geometry("750x350")
        self.TEXT_WRAP_LENGTH = 450

        # Select folder
        self._folder_button = ctk.CTkButton(
            self, text="Select Folder", command=self.select_folder
        )
        self._folder_button.grid(column=1, row=1, padx=10, pady=15)
        self._chosen_directory = ctk.CTkLabel(
            self, text="No folder selected", wraplength=self.TEXT_WRAP_LENGTH
        )
        self._chosen_directory.grid(column=2, row=1, padx=10, pady=15)

        # URL input
        self._url_label = ctk.CTkLabel(self, text="Enter Rutube URL:")
        self._url_label.grid(column=1, row=2, padx=10, pady=10)
        self._url_entry = ctk.CTkEntry(self, width=300)
        self._url_entry.grid(column=2, row=2, padx=10, pady=10)

        # Get video info
        self._fetch_result_label = ctk.CTkLabel(self, text="")
        self._fetch_result_label.grid(column=1, row=3, padx=10, pady=10)

        self._video_info_button = ctk.CTkButton(
            self,
            text="Get Video Info",
            command=self.fetch_video_info,
            state="disabled",
        )
        self._video_info_button.grid(column=2, row=3, padx=10, pady=10)

        # Video title
        self._video_title_static_text = ctk.CTkLabel(self, text="Video Title:")
        self._video_title_static_text.grid(column=1, row=4, padx=10, pady=10)
        self._video_title_dynamic = ctk.CTkLabel(
            self, text="", wraplength=self.TEXT_WRAP_LENGTH
        )
        self._video_title_dynamic.grid(column=2, row=4, padx=10, pady=10)

        # Dropdown for qualities
        self._dropdown = ctk.CTkComboBox(self, state="readonly")
        self._dropdown.grid(column=1, row=5, padx=10, pady=10)

        # Download button
        self._download_button = ctk.CTkButton(
            self,
            text="Download",
            command=self.start_download,
            state="disabled",
        )
        self._download_button.grid(column=2, row=5, padx=10, pady=10)

        # Progress bar
        self._progress_bar = ctk.CTkProgressBar(self)
        self._progress_bar.grid(
            column=2, row=6, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        self._progress_bar.set(0)

    def _update_bar(self, progress_bar_value: int) -> None:
        if progress_bar_value == 100 and self._download:
            self._progress_bar.set(1)
            messagebox.showinfo("Download Complete", "Download Complete")
            self._download = None
        else:
            self._progress_bar.set(progress_bar_value / 100)
            self.after(self._refresh_ms, self._poll_queue)

    def _poll_queue(self) -> None:
        if not self._queue.empty():
            percent_complete = self._queue.get()
            self._update_bar(percent_complete)
        else:
            if self._download:
                self.after(self._refresh_ms, self._poll_queue)

    def fetch_video_info(self) -> None:
        self._fetch_result_label.configure(text="")
        if not self._url_entry.get():
            messagebox.showerror("Error", "Enter URL first")
        elif self._upload_directory and self._url_entry.get():
            try:
                self.__fetch_video_info()
                self.__fill_qualities()
                self.__fill_title()
            except (InvalidURLError, KeyError):
                self._fetch_result_label.configure(
                    text="Invalid URL", text_color="red"
                )
            except (APIResponseError, MasterPlaylistInitializationError):
                self._fetch_result_label.configure(
                    text="Wrong URL or Connection fail", text_color="red"
                )

    def __fetch_video_info(self) -> None:
        if not self._upload_directory:
            raise UploadDirectoryNotSelectedError
        self._download = Downloader(
            self._url_entry.get(),
            self._loop,
            self._queue.put,
            self._upload_directory,
            self._session,
        )
        download_future = asyncio.run_coroutine_threadsafe(
            self._download.fetch_video_info(), self._loop
        )
        self._download_available_qualities = download_future.result()

    def __fill_qualities(self) -> None:
        fields = [
            f"{x}x{y}" for x, y in self._download_available_qualities.keys()
        ]
        self._dropdown.configure(values=fields)
        self._dropdown.set(fields[-1])

    def __fill_title(self) -> None:
        if self._download:
            self._video_title_dynamic.configure(
                text=self._download.video_title
            )

    def start_download(self) -> None:
        if self._download:
            self.__set_quality()
            asyncio.run_coroutine_threadsafe(
                self._download.download_video(), self._loop
            )
            self.after(self._refresh_ms, self._poll_queue)

    def __set_quality(self) -> None:
        if self._download is None:
            raise DownloaderIsNotInitializerError(
                "You must initialize Downloader object first."
            )
        selected_quality = tuple(map(int, self._dropdown.get().split("x")))
        quality_future = asyncio.run_coroutine_threadsafe(
            self._download.select_quality(selected_quality), self._loop
        )
        quality_future.result()

    def select_folder(self) -> None:
        directory = filedialog.askdirectory(title="Select Download Folder")
        self._chosen_directory.configure(text=directory)
        self._upload_directory = Path(directory)
        if not self._upload_directory.is_dir():
            raise ValueError("Selected folder does not exist")
        self._download_button.configure(state="normal")
        self._video_info_button.configure(state="normal")

if __name__ == "__main__":
    app = DownloaderUI()
    app.mainloop()
