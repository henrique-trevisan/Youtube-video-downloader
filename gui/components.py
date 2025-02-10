import customtkinter as ctk

class MyScrollableRadioButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title, values, variable):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        self.values = values
        self.radiobuttons = []
        self.variable = variable

        # Filtering combo boxes
        self.audio_video_filter = ctk.CTkComboBox(self, values=["Audio", "Video"])
        self.audio_video_filter.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.format_filter = ctk.CTkComboBox(self, values=["MP4", "MP3", "WEBM", "MKV"])
        self.format_filter.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.audio_quality_filter = ctk.CTkComboBox(self, values=["High", "Medium", "Low"])
        self.audio_quality_filter.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.video_quality_filter = ctk.CTkComboBox(self, values=["1080p", "720p", "480p", "360p"])
        self.video_quality_filter.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Add radio buttons
        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, variable=self.variable, value=value)
            radiobutton.grid(row=i + 1, column=0, columnspan=4, padx=10, pady=(10, 0), sticky="ew")
            self.radiobuttons.append(radiobutton)
