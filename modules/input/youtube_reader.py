import os
import subprocess
from uuid import uuid4
from datetime import datetime

from .base_reader import AbstractReader
from .file_reader import FileReader


class YouTubeReader(AbstractReader):
    """
    Reader that downloads a YouTube video to a local file.
    """
    def __init__(self):
        super().__init__()
        # delegate WAV conversion to FileReader
        self._file_reader = FileReader()

    def _download_video(self, url: str) -> str:
        """
        Download a YouTube video using yt-dlp and return the file path.
        """
        output_dir = self.cfg.paths.temp_dir
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_id = str(uuid4())
        filename = f"{timestamp}_{short_id}.mp4"
        output_path = os.path.join(output_dir, filename)

        subprocess.run([
            'yt-dlp',
            '-o', output_path,
            url
        ], check=True)

        return output_path

    def _convert_video_to_wav(self, video_path: str) -> str:
        """
        Delegate wav conversion to FileReader.
        """
        return self._file_reader.convert_to_wav(video_path)

    def convert_to_wav(self, url: str) -> str:
        """
        Download a YouTube URL and convert it to wav, returning the wav filename.
        """
        video_path = self._download_video(url)
        return self._convert_video_to_wav(video_path)
