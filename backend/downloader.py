"""Video search and download utilities."""

from pathlib import Path
import shutil

import yt_dlp


class Downloader:
    """Utility class for searching and downloading YouTube videos."""

    @staticmethod
    def _get_ffmpeg_dir() -> Path | None:
        """Return path to the bundled FFmpeg directory if available."""
        ffmpeg_dir = (
            Path(__file__).resolve().parent.parent
            / "thirdParty"
            / "ffmpeg"
            / "bin"
        )
        return ffmpeg_dir if ffmpeg_dir.exists() else None

    @staticmethod
    def search_video(url: str) -> dict:
        """Return video information without downloading."""
        ydl_opts = {
            "quiet": True,
            "simulate": True,
            "force_generic_extractor": True,
        }
        ffmpeg_dir = Downloader._get_ffmpeg_dir()
        if ffmpeg_dir and not shutil.which("ffmpeg"):
            ydl_opts["ffmpeg_location"] = str(ffmpeg_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    @staticmethod
    def download_video(
        info: dict,
        format_id: str,
        save_path: str,
        progress_callback=None,
        finished_callback=None,
    ) -> None:
        """Download the selected format to the given path."""

        def _hook(d):
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                if progress_callback and total:
                    progress_callback(downloaded / total)
            elif d.get("status") == "finished":
                if progress_callback:
                    progress_callback(1.0)
                if (
                    d.get("info_dict", {}).get("requested_formats") is None
                    and finished_callback
                ):
                    finished_callback()

        def _pp_hook(d):
            if (
                d.get("status") == "finished"
                and "merger" in d.get("postprocessor", "").lower()
            ):
                if finished_callback:
                    finished_callback()

        output_template = Path(save_path) / "%(title)s.%(ext)s"
        ydl_opts = {
            "format": format_id.split(" - ")[0],
            "outtmpl": str(output_template),
            "progress_hooks": [_hook],
            "postprocessor_hooks": [_pp_hook],
        }
        ffmpeg_dir = Downloader._get_ffmpeg_dir()
        if ffmpeg_dir and not shutil.which("ffmpeg"):
            ydl_opts["ffmpeg_location"] = str(ffmpeg_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info["webpage_url"]])
