import yt_dlp

class Downloader:
    @staticmethod
    def search_video(url):
        ydl_opts = {
            'quiet': True,
            'simulate': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    @staticmethod
    def download_video(info, format_id):
        ydl_opts = {
            'format': format_id,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info['webpage_url']])
