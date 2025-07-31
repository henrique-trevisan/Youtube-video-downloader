from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import threading

class Downloader:
    @staticmethod
    def search_video(url: str):
        """Return a ``YouTube`` object for the provided URL."""
        return YouTube(url)

    @staticmethod
    def download_video(yt: YouTube, format_id: str, save_path: str):
        """Download the selected stream using ``pytube``.

        If the selected stream does not contain audio, the best available audio
        stream is downloaded in parallel and merged using ``moviepy``.
        """

        itag = format_id.split(" - ")[0]
        stream = yt.streams.get_by_itag(int(itag))
        if stream is None:
            raise ValueError("Invalid stream selection")

        if stream.is_progressive or stream.includes_audio_track:
            stream.download(output_path=save_path)
            return

        video_path = os.path.join(save_path, "video_temp.mp4")
        audio_path = os.path.join(save_path, "audio_temp.mp4")
        result = {}

        def download_video_stream():
            result['video'] = stream.download(output_path=save_path, filename=os.path.basename(video_path))

        def download_audio_stream():
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            result['audio'] = audio_stream.download(output_path=save_path, filename=os.path.basename(audio_path))

        t_video = threading.Thread(target=download_video_stream)
        t_audio = threading.Thread(target=download_audio_stream)
        t_video.start()
        t_audio.start()
        t_video.join()
        t_audio.join()

        final_path = os.path.join(save_path, f"{yt.title}.mp4")

        def merge_streams():
            video_clip = VideoFileClip(result['video'])
            audio_clip = AudioFileClip(result['audio'])
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(final_path, codec='libx264', audio_codec='aac')
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            os.remove(result['video'])
            os.remove(result['audio'])

        t_merge = threading.Thread(target=merge_streams)
        t_merge.start()
        t_merge.join()
