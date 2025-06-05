"""Helper utilities for the application."""

import json
from pathlib import Path
from tkinter import filedialog


CONFIG_DIR = Path.home() / ".config" / "yt_downloader"
CONFIG_FILE = CONFIG_DIR / "settings.json"


def load_last_save_path() -> str | None:
    """Return the previously saved download directory if available."""
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("save_path")
    except FileNotFoundError:
        return None
    except Exception:
        return None


def save_last_save_path(path: str) -> None:
    """Persist the provided download directory path."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump({"save_path": path}, f)
    except Exception:
        pass


def change_save_path(entry_widget) -> None:
    """Prompt the user for a directory and update the entry widget."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, folder_selected)
        save_last_save_path(folder_selected)
