import customtkinter as ctk
from tkinter import filedialog
from gui.components import MyScrollableRadioButtonFrame
from backend.downloader import Downloader
from utils.helpers import change_save_path
import threading, queue

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("700x600")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.GUI_oppened = True

        self.task_queue = queue.Queue()
        self.worker = threading.Thread(target=self.worker_thread, daemon=True)
        self.worker.start()

        self.selected_format = ctk.StringVar()
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox_var.set(True)

        self.init_gui()

    def init_gui(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure([1, 2], weight=0)

        # Save Path Frame
        self.Save_Frame = ctk.CTkFrame(self, corner_radius=0)
        self.Save_Frame.grid(row=1, column=0, sticky="nwe")
        self.Save_Frame.grid_columnconfigure(0, weight=0)
        self.Save_Frame.grid_columnconfigure(1, weight=2)
        self.Save_Frame.grid_columnconfigure(2, weight=0)

        self.Save_Label = ctk.CTkLabel(self.Save_Frame, text="Save to: ")
        self.Save_Label.grid(row=0, column=0, padx=[20, 5], pady=20, sticky="w")

        self.Save_Entry = ctk.CTkEntry(self.Save_Frame, placeholder_text="File path")
        self.Save_Entry.grid(row=0, column=1, padx=[0, 5], pady=20, sticky="ew")

        change_button_text = "Change"
        self.Save_Button = ctk.CTkButton(self.Save_Frame, text=change_button_text, 
                                         command=lambda: change_save_path(self.Save_Entry))
        self.Save_Button.grid(row=0, column=2, padx=[0, 20], pady=20, sticky="e")

        # URL Frame
        self.URL_Frame = ctk.CTkFrame(self, corner_radius=0)
        self.URL_Frame.grid(row=2, column=0, sticky="nwe")
        self.URL_Frame.grid_columnconfigure(0, weight=2)
        self.URL_Frame.grid_columnconfigure([1, 2], weight=0)

        self.URL_Label = ctk.CTkLabel(self, text="YouTube Video Downloader", font=("Consolas", 24))
        self.URL_Label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.URL_Entry = ctk.CTkEntry(self.URL_Frame, placeholder_text="Video URL")
        self.URL_Entry.grid(row=1, column=0, padx=[20, 5], pady=20, sticky="ew")

        self.Paste_URL_Button = ctk.CTkButton(
            self.URL_Frame, text="Paste URL", 
            command=lambda: self.URL_Entry.insert(0, self.clipboard_get())
        )
        self.Paste_URL_Button.grid(row=1, column=1, padx=[0, 5], pady=20, sticky="e")

        self.Clear_URL_Button = ctk.CTkButton(
            self.URL_Frame, text="Clear URL", 
            command=lambda: self.URL_Entry.delete(0, "end")
        )
        self.Clear_URL_Button.grid(row=1, column=2, padx=[0, 20], pady=20, sticky="w")

        self.Search_Button = ctk.CTkButton(self.URL_Frame, text="Search Video", command=self.search_video)
        self.Search_Button.grid(row=2, column=0, padx=20, pady=[0, 20], columnspan=3)

    def search_video(self):
        url = self.URL_Entry.get()
        if not url:
            self.show_error_message("Invalid URL. Please try again.")
            return
        try:
            info = Downloader.search_video(url)
            self.display_streams(info)
        except Exception as e:
            self.show_error_message("Video not found. Please check the URL and try again.")

    def display_streams(self, info):
        formats = info.get("formats", [])
        format_values = [
            f"{fmt.get('format_id')} - {fmt.get('ext')} - {fmt.get('resolution', 'audio only')}" 
            for fmt in formats
        ]

        stream_frame = MyScrollableRadioButtonFrame(
            self, title="Available Streams", values=format_values, variable=self.selected_format
        )
        stream_frame.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsew")

    def show_error_message(self, message):
        error_label = ctk.CTkLabel(self, text=message, text_color="red")
        error_label.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")

    def on_closing(self):
        self.GUI_oppened = False
        self.destroy()

    def worker_thread(self):
        while self.GUI_oppened:
            try:
                func, args = self.task_queue.get(timeout=1)
                func(*args)
                self.task_queue.task_done()
            except queue.Empty:
                pass
