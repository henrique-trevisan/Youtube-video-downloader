"""Main application window."""

import queue

import customtkinter as ctk

from backend.downloader import Downloader
from backend.worker import Worker
from gui.components import (
    MyScrollableRadioButtonFrame,
    MyYouTubeDownloaderApp,
)
from utils.helpers import save_last_save_path


class App(ctk.CTk):
    """Graphical interface for the downloader."""

    def __init__(self) -> None:
        """Configure the main window and worker threads."""
        super().__init__()
        self.geometry("700x630")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.gui_opened = True

        self.task_queue = queue.Queue()
        self.worker = Worker(self.task_queue, self.gui_opened)

        self.selected_format = ctk.StringVar()
        self.selected_format.set(True)
        self.selected_format.trace_add("write", self.update_download_button)
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox_var.set(True)

        # flag to indicate an ongoing download
        self.downloading = False
        # stores info about the last searched video
        self.video_info: dict | None = None

        self.message_label = None
        MyYouTubeDownloaderApp(self)

        # progress bar for downloads, hidden by default
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(
            row=6,
            column=0,
            padx=10,
            pady=(0, 20),
            sticky="ew",
        )
        self.progress_bar.grid_remove()

    def search_video(self) -> None:
        """Retrieve video information and display available streams."""
        self.show_message("Searching for video...")
        url = self.URL_Entry.get()
        if not url:
            self.show_message("Invalid URL. Please try again.", "red")
            return
        try:
            info = Downloader.search_video(url)
            self.video_info = info
            self.display_streams(info)
            self.show_message("Video found. Select a stream to download.")
        except Exception:
            self.show_message(
                "Video not found. Please check the URL and try again."
            )

    def display_streams(self, info: dict) -> None:
        """Show available streams in a scrollable frame."""
        format_values = [
            (f"{display} - {info.get('title', '')}", fmt)
            for display, fmt in Downloader.available_streams(info)
        ]

        stream_frame = MyScrollableRadioButtonFrame(
            self,
            title="Available Streams",
            values=format_values,
            variable=self.selected_format,
        )
        stream_frame.grid(
            row=3,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
        )

        self.download_button = ctk.CTkButton(
            self,
            text="Download",
            command=self.start_download,
            state="disabled",
        )
        self.download_button.grid(
            row=5,
            column=0,
            padx=10,
            pady=10,
            sticky="ew",
        )

    def update_download_button(self, *args) -> None:
        """Enable or disable download button based on selection."""
        if self.selected_format.get() and not self.downloading:
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")

    def start_download(self) -> None:
        """Disable the button and queue the download task."""
        self.download_button.configure(state="disabled")
        self.task_queue.put((self._download_task, ()))

    def _download_task(self) -> None:
        """Worker thread entry to download the selected stream."""
        selected_stream = self.selected_format.get()
        save_path = self.Save_Entry.get()
        if not selected_stream or not save_path or not self.video_info:
            self.show_message(
                "Please select a stream and save path before downloading."
            )
            return
        self.download_button.configure(state="disabled")
        self.downloading = True
        self.progress_bar.set(0)
        self.progress_bar.grid()
        self.show_message("Starting download...", "green")
        Downloader.download_video(
            self.video_info,
            selected_stream,
            save_path,
            self._progress_callback,
            self._download_finished_callback,
            self._stage_callback,
        )

    def show_message(self, message: str, color: str = "white") -> None:
        """Display a status message on the main window."""
        if self.message_label:
            self.message_label.destroy()
        self.message_label = ctk.CTkLabel(self, text=message, text_color=color)
        self.message_label.grid(
            row=4,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew",
        )

    def _progress_callback(self, progress: float) -> None:
        """Thread-safe update of the progress bar."""
        self.after(0, lambda p=progress: self.progress_bar.set(p))

    def _stage_callback(self, stage: str) -> None:
        """Thread-safe update of the status message."""
        self.after(0, lambda s=stage: self.show_message(s, "green"))

    def _download_finished_callback(self) -> None:
        """Schedule UI updates when a download completes."""
        self.after(0, self._on_download_finished)

    def _on_download_finished(self) -> None:
        """Re-enable UI elements and show completion message."""
        self.downloading = False
        # restore download button state based on current selection
        self.update_download_button()
        self.progress_bar.grid_remove()
        self.show_message("Download finished!", "green")

    def on_closing(self) -> None:
        """Handle the window close event."""
        self.gui_opened = False
        self.worker.stop_workers(self.gui_opened)
        save_last_save_path(self.Save_Entry.get())
        self.destroy()
