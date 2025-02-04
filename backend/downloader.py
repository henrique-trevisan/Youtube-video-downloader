import yt_dlp
import os

class Downloader:
    @staticmethod
    def search_video(url: str):
        ydl_opts = {
            'quiet': True,
            'simulate': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    @staticmethod
    def download_video(info: dict, format_id: dict, save_path):
        ydl_opts = {
            'format': format_id.split(' - ')[0],
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info['webpage_url']])