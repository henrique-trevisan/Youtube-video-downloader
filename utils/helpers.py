from tkinter import filedialog

def change_save_path(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, folder_selected)
