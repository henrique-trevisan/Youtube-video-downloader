"""GUI components for the downloader application."""

import customtkinter as ctk
from utils.helpers import change_save_path, load_last_save_path


class MyScrollableRadioButtonFrame(ctk.CTkScrollableFrame):
    """Scrollable frame with radio buttons and filters."""

    def __init__(self, master, title, values, variable) -> None:
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = list(values)
        self.radiobuttons = []
        self.variable = variable

        # Initial radio buttons
        self.create_radio_buttons(self.values)

    def create_radio_buttons(self, values: list[str]) -> None:
        """Create radiobutton widgets for the given value list."""
        for rb in self.radiobuttons:
            rb.destroy()
        self.radiobuttons = []
        for i, value in enumerate(values):
            radiobutton = ctk.CTkRadioButton(
                self,
                text=value,
                variable=self.variable,
                value=value,
            )
            radiobutton.grid(
                row=i,
                column=0,
                padx=10,
                pady=(5 if i else 0, 5),
                sticky="ew",
            )
            self.radiobuttons.append(radiobutton)


class MyYouTubeDownloaderApp(ctk.CTk):
    """Container widget for the downloader widgets."""

    def __init__(self, master) -> None:
        self.master = master
        self.init_gui()

    def init_gui(self) -> None:
        """Create and layout all GUI widgets."""
        # Configure grid
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure([1, 2], weight=0)

        # Save Path Frame
        self.master.Save_Frame = ctk.CTkFrame(self.master, corner_radius=0)
        self.master.Save_Frame.grid(row=1, column=0, sticky="nwe")
        self.master.Save_Frame.grid_columnconfigure(0, weight=0)
        self.master.Save_Frame.grid_columnconfigure(1, weight=2)
        self.master.Save_Frame.grid_columnconfigure(2, weight=0)

        self.master.Save_Label = ctk.CTkLabel(
            self.master.Save_Frame,
            text="Save to: ",
        )
        self.master.Save_Label.grid(
            row=0,
            column=0,
            padx=[20, 5],
            pady=20,
            sticky="w",
        )

        self.master.Save_Entry = ctk.CTkEntry(
            self.master.Save_Frame,
            placeholder_text="File path",
        )
        last_path = load_last_save_path()
        if last_path:
            self.master.Save_Entry.insert(0, last_path)
        self.master.Save_Entry.grid(
            row=0,
            column=1,
            padx=[0, 5],
            pady=20,
            sticky="ew",
        )

        change_button_text = "Change"
        self.master.Save_Button = ctk.CTkButton(
            self.master.Save_Frame,
            text=change_button_text,
            command=lambda: change_save_path(self.master.Save_Entry),
        )
        self.master.Save_Button.grid(
            row=0,
            column=2,
            padx=[0, 20],
            pady=20,
            sticky="e",
        )

        # URL Frame
        self.master.URL_Frame = ctk.CTkFrame(self.master, corner_radius=0)
        self.master.URL_Frame.grid(row=2, column=0, sticky="nwe")
        self.master.URL_Frame.grid_columnconfigure(0, weight=2)
        self.master.URL_Frame.grid_columnconfigure([1, 2], weight=0)

        self.master.URL_Label = ctk.CTkLabel(
            self.master,
            text="YouTube Video Downloader",
            font=("Consolas", 24),
        )
        self.master.URL_Label.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
        )

        self.master.URL_Entry = ctk.CTkEntry(
            self.master.URL_Frame,
            placeholder_text="Video URL",
        )
        self.master.URL_Entry.grid(
            row=1,
            column=0,
            padx=[20, 5],
            pady=20,
            sticky="ew",
        )

        self.master.Paste_URL_Button = ctk.CTkButton(
            self.master.URL_Frame,
            text="Paste URL",
            command=lambda: self.master.URL_Entry.insert(
                0,
                self.master.clipboard_get(),
            ),
        )
        self.master.Paste_URL_Button.grid(
            row=1,
            column=1,
            padx=[0, 5],
            pady=20,
            sticky="e",
        )

        self.master.Clear_URL_Button = ctk.CTkButton(
            self.master.URL_Frame,
            text="Clear URL",
            command=lambda: self.master.URL_Entry.delete(0, "end"),
        )
        self.master.Clear_URL_Button.grid(
            row=1,
            column=2,
            padx=[0, 20],
            pady=20,
            sticky="w",
        )

        self.master.Search_Button = ctk.CTkButton(
            self.master.URL_Frame,
            text="Search Video",
            command=lambda: self.master.task_queue.put(
                (self.master.search_video, ())
            ),
        )
        self.master.Search_Button.grid(
            row=2,
            column=0,
            padx=20,
            pady=[0, 20],
            columnspan=3,
        )
