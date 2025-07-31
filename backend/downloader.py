"""Video search and download utilities."""

from pathlib import Path
import shutil
import os
import subprocess

import yt_dlp


def _best_audio_id(formats: list[dict]) -> str:
    """Return the format_id of the best available audio stream."""
    audio_formats = [
        f
        for f in formats
        if f.get("acodec") != "none" and f.get("vcodec") == "none"
    ]
    best_audio = max(
        audio_formats,
        key=lambda f: (
            f.get("language_preference", 0),
            f.get("abr") or f.get("tbr") or 0,
        ),
        default=None,
    )
    return best_audio.get("format_id") if best_audio else "bestaudio"


def _best_video_formats(formats: list[dict]) -> list[tuple[str, str]]:
    """Return video formats sorted by height descending."""
    video_formats = [f for f in formats if f.get("vcodec") != "none"]
    best_by_height: dict[int, dict] = {}
    for fmt in video_formats:
        height = fmt.get("height")
        if not height:
            continue
        current = best_by_height.get(height)
        if not current or (fmt.get("tbr") or 0) > (current.get("tbr") or 0):
            best_by_height[height] = fmt
    audio_id = _best_audio_id(formats)
    return [
        (
            f"{fmt.get('resolution')}",
            f"{fmt['format_id']}+{audio_id}",
        )
        for _, fmt in sorted(best_by_height.items(), reverse=True)
    ]


def _hwaccel_args(ffmpeg_path: str) -> list[str]:
    """Return ffmpeg hardware acceleration args when supported."""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-hwaccels"],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return []

    available = {
        line.strip().lower()
        for line in result.stdout.splitlines()
        if line.strip() and not line.lower().startswith("hardware")
    }
    priority = [
        "d3d11va",
        "dxva2",
        "cuda",
        "qsv",
        "vaapi",
        "vdpau",
        "videotoolbox",
    ]
    for method in priority:
        if method in available:
            return ["-hwaccel", method]
    return []


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
    def available_streams(info: dict) -> list[tuple[str, str]]:
        """Return formatted stream options for the given info."""
        return _best_video_formats(info.get("formats", []))

    @staticmethod
    def _build_ydl_opts(format_id: str, output: Path) -> dict:
        """Return common yt-dlp options with ffmpeg settings."""
        format_id = format_id.split(" - ")[0]
        ydl_opts = {
            "format": format_id,
            "outtmpl": str(output),
            "concurrent_fragment_downloads": os.cpu_count() or 1,
            "restrictfilenames": True,
            "merge_output_format": "mkv",  # evita erro ao mesclar Opus
            "verbose": True,
        }
        ffmpeg_path = shutil.which("ffmpeg")
        ffmpeg_dir = Downloader._get_ffmpeg_dir()
        if not ffmpeg_path and ffmpeg_dir:
            ffmpeg_path = str(ffmpeg_dir / "ffmpeg.exe")
            ydl_opts["ffmpeg_location"] = str(ffmpeg_dir)
        if ffmpeg_path:
            hwaccel = _hwaccel_args(ffmpeg_path)
        else:
            hwaccel = []
        ydl_opts["postprocessor_args"] = {
            "Merger+ffmpeg": [
                "-threads",
                str(os.cpu_count() or 1),
                *hwaccel,
            ]
        }
        return ydl_opts


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
        stage_callback=None,
    ) -> None:
        """Download the selected format to the given path."""

        current_stage = [None]

        def _hook(d):
            if d.get("status") == "downloading":
                info_dict = d.get("info_dict", {})
                stage = None
                if info_dict.get("vcodec") != "none" and info_dict.get("acodec") == "none":
                    stage = "Downloading video..."
                elif info_dict.get("acodec") != "none" and info_dict.get("vcodec") == "none":
                    stage = "Downloading audio..."
                if stage_callback and stage and stage != current_stage[0]:
                    current_stage[0] = stage
                    stage_callback(stage)
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
            if "merger" in d.get("postprocessor", "").lower():
                if d.get("status") == "started":
                    if stage_callback:
                        stage_callback("Merging...")
                elif d.get("status") == "finished":
                    if finished_callback:
                        finished_callback()

        output_template = Path(save_path) / "%(title)s.%(ext)s"
        ydl_opts = Downloader._build_ydl_opts(format_id, output_template)
        ydl_opts.update(
            {
                "progress_hooks": [_hook],
                "postprocessor_hooks": [_pp_hook],
            }
        )
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info["webpage_url"]])
