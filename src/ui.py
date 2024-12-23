from asyncio import AbstractEventLoop, new_event_loop
from pathlib import Path
from queue import Queue
from tkinter import Button, Entry, Label, Tk, filedialog, messagebox, ttk
from typing import Optional

from downloader import Downloader
from utils import APIResponseError, InvalidURLError


class DownloaderUI(Tk):
    """
    UI for Rutube Downloader created with tkinter.
    """

    def __init__(
        self,
        loop: AbstractEventLoop = new_event_loop(),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._loop = loop
        self._refresh_ms = 25
        self._queue: Queue = Queue()
        self._download: Optional[Downloader] = None
        self._upload_directory: Optional[Path] = None
        # Ui elements:

        # Basic configure
        self.title("Rutube Downloader")
        self.geometry("750x300")
        self.TEXT_WRAP_LENGTH = 450

        # Select folder
        self._folder_button = Button(
            self, text="Select Folder", command=self.select_folder
        )
        self._folder_button.grid(column=1, row=1, padx=10, pady=15)
        self._chosen_folder = Label(
            self, text="No folder selected", wraplength=self.TEXT_WRAP_LENGTH
        )
        self._chosen_folder.grid(column=2, row=1, padx=10, pady=15)

        # URL input
        self._url_label = Label(self, text="Enter Rutube URL:")
        self._url_label.grid(column=1, row=2, padx=10, pady=10)
        self._url_entry = Entry(self, width=48)
        self._url_entry.grid(column=2, row=2, padx=10, pady=10)

        # Get video info
        self._fetch_result_label = Label(self, text="")
        self._fetch_result_label.grid(column=1, row=3, padx=10, pady=10)

        self._video_info_button = Button(
            self,
            text="Get Video Info",
            command=self.fetch_video_info,
            state="disabled",  # initially disabled
        )
        self._video_info_button.grid(column=2, row=3, padx=10, pady=10)

        # Video title
        self._video_title_static_text = Label(self, text="Video Title:")
        self._video_title_static_text.grid(column=1, row=4, padx=10, pady=10)
        self._video_title_dynamic = Label(
            self, text="", wraplength=self.TEXT_WRAP_LENGTH
        )
        self._video_title_dynamic.grid(column=2, row=4, padx=10, pady=10)

        # Dropdown for qualities
        self._dropdown = ttk.Combobox(self, state="readonly")
        self._dropdown.grid(column=1, row=5, padx=10, pady=10)

        # Download button
        self._download_button = ttk.Button(
            self,
            text="Download",
            command=self.start_download,
            state="disabled",  # initially disabled
        )
        self._download_button.grid(column=2, row=5, padx=10, pady=10)

        # Progress bar
        self._progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=400, mode="determinate"
        )
        self._progress_bar.grid(
            column=2, row=6, columnspan=2, padx=10, pady=10, sticky="ew"
        )

    def _update_bar(self, progress_bar_value: int) -> None:
        """Update the progress bar.
        Call only from main thread."""
        if progress_bar_value == 100 and self._download:
            self._progress_bar["value"] = progress_bar_value
            messagebox.showinfo(
                "Download Complete",
                "Download Complete",
            )  #  a Download Complete" alert show
            # a little bit before last downloaded chunks is actually saved.
            self._download = None
        else:
            self._progress_bar["value"] = progress_bar_value
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

    def fetch_video_info(self) -> None:
        """
        1. Fetch video info from Rutube API
        2. Fill the UI with available qualities or error message.
        """
        self._fetch_result_label.config(text="")
        if not self._url_entry.get():
            messagebox.showerror("Error", "Enter URL first")
        elif self._upload_directory and self._url_entry.get():
            try:
                self._download = Downloader(
                    self._url_entry.get(),
                    self._loop,
                    self._queue_update,
                    upload_directory=self._upload_directory,
                )
                __download_future = self._download.fetch_video_info_from_ui()
                self._download_available_qualities = __download_future.result()
                self.__fill_qualities()
                self.__fill_title()
            except (InvalidURLError, KeyError):
                self._fetch_result_label.config(text="Invalid URL", fg="red")
            except APIResponseError:
                self._fetch_result_label.config(
                    text="Wrong URL or Connection fail", fg="red"
                )

    def __fill_qualities(self) -> None:
        fields = [
            f"{x}x{y}" for x, y in self._download_available_qualities.keys()
        ]
        self._dropdown["values"] = fields
        self._dropdown.current(len(fields) - 1)

    def __fill_title(self) -> None:
        if self._download:
            self._video_title_dynamic.config(text=self._download.video_title)

    def start_download(self) -> None:
        """Download the video from the given URL."""
        if self._download:
            self.__set_quality()
            self._download.download_video_from_ui()
            self.after(self._refresh_ms, self._poll_queue)

    def __set_quality(self) -> None:
        if self._download:
            dict_key = tuple(map(int, self._dropdown.get().split("x")))
            if len(dict_key) != 2:
                raise ValueError(
                    "Invalid quality selected,"
                    " it must be something like: 1280x720"
                )
            self._download.select_quality_from_ui(dict_key).result()

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            print(f"Selected folder: {folder}")
            self._chosen_folder.config(text=folder)
            self._upload_directory = Path(folder)
            if not self._upload_directory.is_dir():
                raise ValueError("Selected folder does not exist")
            self._download_button.config(state="normal")
            self._video_info_button.config(state="normal")
        else:
            raise ValueError("No folder selected")


# Use run_ui.py to start the application
