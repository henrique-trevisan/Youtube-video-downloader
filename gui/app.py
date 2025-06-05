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
        self.geometry("700x610")
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

        self.message_label = None
        MyYouTubeDownloaderApp(self)

    def search_video(self) -> None:
        """Retrieve video information and display available streams."""
        self.show_message("Searching for video...")
        url = self.URL_Entry.get()
        if not url:
            self.show_message("Invalid URL. Please try again.", "red")
            return
        try:
            info = Downloader.search_video(url)
            self.display_streams(info)
            self.show_message("Video found. Select a stream to download.")
        except Exception:
            self.show_message(
                "Video not found. Please check the URL and try again."
            )

    def display_streams(self, info: dict) -> None:
        """Show available streams in a scrollable frame."""
        formats = info.get("formats", [])

        video_formats = [f for f in formats if f.get("vcodec") != "none"]
        audio_formats = [
            f
            for f in formats
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]

        best_audio = max(
            audio_formats,
            key=lambda f: f.get("abr") or f.get("tbr") or 0,
            default=None,
        )
        audio_id = best_audio.get("format_id") if best_audio else "bestaudio"

        best_by_height: dict[int, dict] = {}
        for fmt in video_formats:
            height = fmt.get("height")
            if not height:
                continue
            current = best_by_height.get(height)
            if (
                not current
                or (fmt.get("tbr") or 0) > (current.get("tbr") or 0)
            ):
                best_by_height[height] = fmt

        format_values = [
            f"{fmt['format_id']}+{audio_id} - {fmt.get('ext')}"
            f" - {fmt.get('resolution')}"
            for height, fmt in sorted(best_by_height.items())
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
            command=lambda: self.task_queue.put((self.download_video, ())),
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
        if self.selected_format.get():
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")

    def download_video(self) -> None:
        """Queue a download task for the selected stream."""
        selected_stream = self.selected_format.get()
        save_path = self.Save_Entry.get()
        if not selected_stream or not save_path:
            self.show_message(
                "Please select a stream and save path before downloading."
            )
            return

        info = Downloader.search_video(self.URL_Entry.get())
        self.show_message("Downloading video...", "green")
        self.task_queue.put(
            (Downloader.download_video, (info, selected_stream, save_path))
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

    def on_closing(self) -> None:
        """Handle the window close event."""
        self.gui_opened = False
        self.worker.stop_workers(self.gui_opened)
        save_last_save_path(self.Save_Entry.get())
        self.destroy()
