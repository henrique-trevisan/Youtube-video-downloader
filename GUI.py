import customtkinter as ctk
import threading, queue, os

class App(ctk.CTk):

    def __init__(self) -> None:
        super().__init__()
        self.geometry("400x225")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the close event to the on_closing function
        self.GUI_oppened: bool = True  # Indicates if the GUI is oppened

        # Function execution queue
        # Hold the functions and its arguments
        self.task_queue: queue = queue.Queue()
        # Initialize the threads (totalThreads - usedThreads)
        self.workers = [threading.Thread(target=self.worker).start() for _ in range(os.cpu_count()-threading.active_count())]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a frame for checkboxes
        self.checkboxFrame = ctk.CTkFrame(self)
        self.checkboxFrame.grid(row=0, column=0, sticky="nsw")

        # Place buttons
        self.bt_1 = ctk.CTkButton(self, text="Click-me", command=self.on_button_click)
        self.bt_1.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        # Create a BooleanVar to bind to the checkbox
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox_var.set(True)  # Default state: checked

        # Place checkboxes
        self.chbx_1 = ctk.CTkCheckBox(self.checkboxFrame, text="Option 1", variable=self.checkbox_var)  # Default checked
        self.chbx_1.grid(row=0, column=0, padx=20, pady=[20, 20], sticky="ew")

        self.chbx_2 = ctk.CTkCheckBox(self.checkboxFrame, text="Option 2")
        self.chbx_2.grid(row=1, column=0, padx=20, pady=[20,20], sticky="ew")

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

    def on_button_click(self) -> None:
        self.task_queue.put((print, ("Hello world",)))  # Wrap the function and its arguments in a tuple

# Main loop
if __name__ == "__main__":
    app = App()
    app.mainloop()