import customtkinter as ctk
import threading, queue, os
from tkinter import filedialog
import yt_dlp

class MyScrollableRadioButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title, values, variable):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.radiobuttons = []
        self.variable = variable

        # Add combo boxes for filtering
        self.audio_video_filter = ctk.CTkComboBox(self, values=["Audio", "Video"])
        self.audio_video_filter.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.format_filter = ctk.CTkComboBox(self, values=["MP4", "MP3", "WEBM", "MKV"])
        self.format_filter.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.audio_quality_filter = ctk.CTkComboBox(self, values=["High", "Medium", "Low"])
        self.audio_quality_filter.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.video_quality_filter = ctk.CTkComboBox(self, values=["1080p", "720p", "480p", "360p"])
        self.video_quality_filter.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Add radio buttons for available streams
        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, variable=self.variable, value=value)
            radiobutton.grid(row=i + 1, column=0, columnspan=4, padx=10, pady=(10, 0), sticky="ew")
            self.radiobuttons.append(radiobutton)

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("700x600")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the close event to the on_closing function
        self.GUI_oppened: bool = True  # Indicates if the GUI is oppened

        # Function execution queue
        # Hold the functions and its arguments
        self.task_queue: queue = queue.Queue()
        # Initialize the threads (totalThreads - usedThreads)
        self.workers = [threading.Thread(target=self.worker).start() for _ in range(os.cpu_count()-threading.active_count())]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure([1, 2], weight=0)

        # Create a second frame for the save path
        self.Save_Frame = ctk.CTkFrame(self, corner_radius=0)
        self.Save_Frame.grid(row=1, column=0, sticky="nwe")
        self.Save_Frame.grid_columnconfigure(0, weight=0)
        self.Save_Frame.grid_columnconfigure(1, weight=2)
        self.Save_Frame.grid_columnconfigure(2, weight=0)

        # Add label, entry, and button to the Save_Frame
        self.Save_Label = ctk.CTkLabel(self.Save_Frame, text="Save to: ")
        self.Save_Label.grid(row=0, column=0, padx=[20, 5], pady=20, sticky="w")

        self.Save_Entry = ctk.CTkEntry(self.Save_Frame, placeholder_text="File path")
        self.Save_Entry.grid(row=0, column=1, padx=[0, 5], pady=20, sticky="ew")

        change_button_text = "Change"
        self.Save_Button = ctk.CTkButton(self.Save_Frame, text=change_button_text, command=self.change_save_path, width=len(change_button_text)+4)
        self.Save_Button.grid(row=0, column=2, padx=[0, 20], pady=20, sticky="e")

        # Create a frame for the URL
        self.URL_Frame = ctk.CTkFrame(self, corner_radius=0)
        self.URL_Frame.grid(row=2, column=0, sticky="nwe")
        self.URL_Frame.grid_columnconfigure(0, weight=2)
        self.URL_Frame.grid_columnconfigure([1, 2], weight=0)

        # Create the URL label
        self.URL_Label = ctk.CTkLabel(self, text="Youtube video downloader", font=("consolas", 24))
        self.URL_Label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Create URL entries
        self.URL = ctk.CTkEntry(self.URL_Frame, placeholder_text="Video URL")
        self.URL.grid(row=1, column=0, padx=[20, 5], pady=20, sticky="ew")

        # Place buttons
        paste_URL_button_text = "Paste URL"
        self.paste_URL_button = ctk.CTkButton(self.URL_Frame, text=paste_URL_button_text, command=lambda: self.on_button_click(self.paste_url_func, ), width=len(paste_URL_button_text)+4)
        self.paste_URL_button.grid(row=1, column=1, padx=[0,5], pady=20, sticky="e")

        clear_URL_button_text = "Clear URL"
        self.clear_URL_button = ctk.CTkButton(self.URL_Frame, text=clear_URL_button_text, command=lambda: self.on_button_click(self.clear_url_func,), width=len(clear_URL_button_text)+4)
        self.clear_URL_button.grid(row=1, column=2, padx=[0,20], pady=20, sticky="w")

        self.search_button = ctk.CTkButton(self.URL_Frame, text="Search video", command=self.search_video)
        self.search_button.grid(row=2, column=0, padx=20, pady=[0, 20], columnspan=3)

        # Create a BooleanVar to bind to the checkbox
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox_var.set(True)  # Default state: checked

        # Variable to store selected format
        self.selected_format = ctk.StringVar()

    # Execute every function call into a thread
    def worker(self) -> None:
        while(self.GUI_oppened):
            try:
                # Get a task from the queue with a timeout
                func, args = self.task_queue.get(timeout=1)
                func(*args)  # Execute the function with its arguments
                self.task_queue.task_done()  # Indicate that the task is done
            except queue.Empty:
                continue

    def on_closing(self) -> None:
        self.GUI_oppened = False
        self.destroy()  # Close the window

    def clear_url_func(self) -> None:
        self.URL.delete(0, "end")  # Clears the content of the entry widget

    def paste_url_func(self) -> None:
        self.URL.delete(0, "end")  # Clears the content of the entry widget
        self.URL.insert(0, self.clipboard_get())

    def on_button_click(self, func, *args) -> None:
        self.task_queue.put((func, args))  # Wrap the function and its arguments in a tuple

    def change_save_path(self) -> None:
        folder_selected = filedialog.askdirectory()  # Open file explorer to select folder
        if folder_selected:
            self.Save_Entry.delete(0, "end")  # Clear current text in entry
            self.Save_Entry.insert(0, folder_selected)  # Insert selected folder path

    def search_video(self) -> None:
        url = self.URL.get()
        if not url:
            return
        try:
            ydl_opts = {
                'quiet': True,
                'simulate': True,
                'force_generic_extractor': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.display_streams(info)
        except Exception as e:
            print(f"Error: {e}")

    def display_streams(self, info: dict) -> None:
        formats = info.get('formats', [])
        format_values = [f"{fmt.get('format_id')} - {fmt.get('ext')} - {fmt.get('resolution', 'audio only')}" for fmt in formats]

        scrollable_frame = MyScrollableRadioButtonFrame(self, title="Available Streams", values=format_values, variable=self.selected_format)
        scrollable_frame.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsew")

# Main loop
if __name__ == "__main__":
    app = App()
    app.mainloop()
