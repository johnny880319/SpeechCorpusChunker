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
        # use placeholder for extension, let yt-dlp choose proper ext
        filename_tmpl = f"{timestamp}_{short_id}.%(ext)s"
        output_template = os.path.join(output_dir, filename_tmpl)

        try:
            subprocess.run([
                'yt-dlp',
                '-o', output_template,
                url
            ], check=True)
        except FileNotFoundError:
            raise FileNotFoundError(
                "yt-dlp 執行檔未找到，請先透過 'pip install yt-dlp' 安裝並確認可執行於 PATH 中。"
            )

        # locate the actual downloaded file with correct extension
        for fname in os.listdir(output_dir):
            if fname.startswith(f"{timestamp}_{short_id}."):
                return os.path.join(output_dir, fname)
        raise RuntimeError(f"下載完成但找不到檔案: {timestamp}_{short_id}")

    def _convert_video_to_wav(self, video_path: str) -> str:
        """
        Delegate wav conversion to FileReader.
        """
        return self._file_reader.convert_to_wav(video_path)

    def download(self, url: str) -> str:
        """
        Download a YouTube video and return the local file path.
        """
        return self._download_video(url)

    def convert_to_wav(self, url: str) -> str:
        """
        Download a YouTube URL and convert it to wav, returning the wav filename.
        """
        video_path = self._download_video(url)
        return self._convert_video_to_wav(video_path)
