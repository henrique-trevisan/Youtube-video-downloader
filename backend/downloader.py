"""Video search and download utilities."""

from pathlib import Path
import shutil
import threading
import subprocess
import tempfile

from pytube import YouTube


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
        """Return basic video information using pytube."""
        try:
            yt = YouTube(url)
        except Exception as exc:  # network errors, invalid URLs, etc
            raise ValueError("Unable to retrieve video information") from exc

        info = {
            "title": yt.title,
            "webpage_url": url,
            "formats": [],
        }

        for stream in yt.streams.filter(adaptive=True):
            fmt = {
                "format_id": str(stream.itag),
                "vcodec": stream.video_codec or "none",
                "acodec": stream.audio_codec or "none",
                "resolution": stream.resolution,
                "abr": int(stream.abr.replace("kbps", "")) if stream.abr else None,
                "tbr": int(stream.bitrate / 1000) if stream.bitrate else None,
                "height": int(stream.resolution.rstrip("p")) if stream.resolution else None,
                "language_preference": 0,
            }
            info["formats"].append(fmt)
        return info

    @staticmethod
    def download_video(
        info: dict,
        format_id: str,
        save_path: str,
        progress_callback=None,
        finished_callback=None,
    ) -> None:
        """Download the selected format to the given path using pytube."""

        try:
            yt = YouTube(info["webpage_url"])
        except Exception as exc:
            raise ValueError("Unable to retrieve video") from exc

        ids = format_id.split("+")
        video_stream = yt.streams.get_by_itag(int(ids[0]))
        audio_stream = yt.streams.get_by_itag(int(ids[1])) if len(ids) > 1 else None

        tmp_dir = tempfile.TemporaryDirectory()
        video_file = Path(tmp_dir.name) / "video.mp4"
        audio_file = Path(tmp_dir.name) / "audio.mp4"

        total_size = (video_stream.filesize or 0) + ((audio_stream.filesize or 0) if audio_stream else 0)
        progress = {"video": 0, "audio": 0}

        def make_callback(key):
            def _cb(stream, chunk, bytes_remaining):
                progress[key] = stream.filesize - bytes_remaining
                if progress_callback and total_size:
                    downloaded = progress["video"] + progress.get("audio", 0)
                    progress_callback(downloaded / total_size)
            return _cb

        threads = []
        threads.append(
            threading.Thread(
                target=video_stream.download,
                kwargs={
                    "output_path": tmp_dir.name,
                    "filename": "video",
                    "on_progress_callback": make_callback("video"),
                },
            )
        )
        if audio_stream:
            threads.append(
                threading.Thread(
                    target=audio_stream.download,
                    kwargs={
                        "output_path": tmp_dir.name,
                        "filename": "audio",
                        "on_progress_callback": make_callback("audio"),
                    },
                )
            )

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        ffmpeg_bin = shutil.which("ffmpeg")
        ffmpeg_dir = Downloader._get_ffmpeg_dir()
        if not ffmpeg_bin and ffmpeg_dir:
            ffmpeg_bin = str(Path(ffmpeg_dir) / "ffmpeg")

        output_file = Path(save_path) / f"{yt.title}.mp4"

        def merge():
            if audio_stream:
                subprocess.run(
                    [
                        ffmpeg_bin,
                        "-y",
                        "-i",
                        str(video_file),
                        "-i",
                        str(audio_file),
                        "-c",
                        "copy",
                        str(output_file),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                shutil.move(str(video_file), str(output_file))
            tmp_dir.cleanup()
            if finished_callback:
                finished_callback()

        merge_thread = threading.Thread(target=merge)
        merge_thread.start()
        merge_thread.join()
