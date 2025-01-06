import customtkinter as ctk

class App(ctk.CTk):

    def __init__(self) -> None:
        super().__init__()
        self.geometry("400x225")
        self.resizable(True, True)
        self.grid_columnconfigure([0, 1], weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.bt_1 = ctk.CTkButton(self, text="Click-me", command=self.on_button_click)
        self.bt_1.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

        self.chbx_1 = ctk.CTkCheckBox(self, text="Option 1")
        self.chbx_1.grid(row=1, column=0, padx=20, pady=[20, 20], sticky="ew")

        self.chbx_2 = ctk.CTkCheckBox(self, text="Option 2")
        self.chbx_2.grid(row=1, column=1, padx=20, pady=[20,20], sticky="ew")

    def on_button_click(self) -> None:
        print("Button pressed")


# Main loop
app = App()
app.mainloop()