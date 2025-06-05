"""Video search and download utilities."""

from pathlib import Path

import yt_dlp


class Downloader:
    """Utility class for searching and downloading YouTube videos."""

    @staticmethod
    def search_video(url: str) -> dict:
        """Return video information without downloading."""
        ydl_opts = {
            "quiet": True,
            "simulate": True,
            "force_generic_extractor": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    @staticmethod
    def download_video(info: dict, format_id: str, save_path: str) -> None:
        """Download the selected format to the given path."""
        output_template = Path(save_path) / "%(title)s.%(ext)s"
        ydl_opts = {
            "format": format_id.split(" - ")[0],
            "outtmpl": str(output_template),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info["webpage_url"]])
