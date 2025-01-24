import customtkinter as ctk
import threading, queue, os

class App(ctk.CTk):
    
    def __init__(self) -> None:
        super().__init__()
        #self.geometry("600x225")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the close event to the on_closing function
        self.GUI_oppened: bool = True  # Indicates if the GUI is oppened

        # Function execution queue
        # Hold the functions and its arguments
        self.task_queue: queue = queue.Queue()
        # Initialize the threads (totalThreads - usedThreads)
        self.workers = [threading.Thread(target=self.worker).start() for _ in range(os.cpu_count()-threading.active_count())]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create a frame for the URL
        self.URL_Frame = ctk.CTkFrame(self)
        self.URL_Frame.grid(row=1, column=0, sticky="nwe")
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

        self.search_button = ctk.CTkButton(self.URL_Frame, text="Search video")
        self.search_button.grid(row=2, column=0, padx=20, pady=[0, 20], columnspan=3)

        # Create a BooleanVar to bind to the checkbox
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox_var.set(True)  # Default state: checked

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
        app.destroy()  # Close the window

    def clear_url_func(self) -> None:
        self.URL.delete(0, "end")  # Clears the content of the entry widget

    def paste_url_func(self) -> None:
        self.URL.delete(0, "end")  # Clears the content of the entry widget
        self.URL.insert(0, self.clipboard_get())

    def on_button_click(self, func, *args) -> None:
        self.task_queue.put((func, args))  # Wrap the function and its arguments in a tuple

# Main loop
if __name__ == "__main__":
    app = App()
    app.mainloop()