import customtkinter as ctk
from gui.components import MyScrollableRadioButtonFrame
from backend.downloader import Downloader
from backend.worker import Worker
from utils.helpers import change_save_path
import queue

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("700x610")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.GUI_oppened = True

        self.task_queue = queue.Queue()
        self.worker = Worker(self.task_queue, self.GUI_oppened)

        self.selected_format = ctk.StringVar()
        self.selected_format.set(True)
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox_var.set(True)

        self.selected_format = ctk.StringVar()
        self.selected_format.trace_add("write", self.update_download_button)

        self.message_label = None  # Placeholder for messages
        self.init_gui()

    def init_gui(self) -> None:
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

        self.Search_Button = ctk.CTkButton(self.URL_Frame, text="Search Video", command=lambda: self.task_queue.put((self.search_video, ())))
        self.Search_Button.grid(row=2, column=0, padx=20, pady=[0, 20], columnspan=3)

    def search_video(self):
        self.show_message("Searching for video...")
        url = self.URL_Entry.get()
        if not url:
            self.show_message("Invalid URL. Please try again.", "red")
            return
        try:
            info = Downloader.search_video(url)
            self.display_streams(info)
            self.show_message("Video found. Select a stream to download.")
        except Exception as e:
            self.show_message("Video not found. Please check the URL and try again.")

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

        self.download_button = ctk.CTkButton(
            self, text="Download", command=self.download_video, state="disabled"
        )
        self.download_button.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

    def update_download_button(self, *args):
        if self.selected_format.get():
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")

    def download_video(self):
        selected_stream = self.selected_format.get()
        save_path = self.Save_Entry.get()
        if not selected_stream or not save_path:
            self.show_message("Please select a stream and save path before downloading.")
            return
        
        info = Downloader.search_video(self.URL_Entry.get())
        self.task_queue.put((Downloader.download_video, (info, selected_stream, save_path)))

    def show_message(self, message, color = "white"):
        if self.message_label:
            self.message_label.destroy()
        self.message_label = ctk.CTkLabel(self, text=message, text_color=color)
        self.message_label.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")

    def on_closing(self):
        self.GUI_oppened = False
        self.worker.stop_workers(self.GUI_oppened)  # Ensure worker threads exit
        self.destroy()