from uuid import uuid4
from datetime import datetime
import time
import os
import subprocess
import torchaudio

# my module
from .base_reader import AbstractReader


class FileReader(AbstractReader):
    """
    FileReader class for reading data from files, including wav, mp3, mp4.
    """
    def __init__(self):
        """
        Initialize the file reader.
        """
        super().__init__()
    

    def convert_to_wav(self, file_path):
        """
        Convert a file to wav format at 16kHz.
        :param file_path: Path to the input file.
        :return: Name of the converted wav file.
        """
        temp_file_path = self.cfg.paths.converted_wav_dir

        # Generate a unique filename using timestamp and UUID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_id = str(uuid4())
        temp_file_name = f"{timestamp}_{short_id}.wav"

        # Build output path and check collision
        output_path = os.path.join(temp_file_path, temp_file_name)
        if os.path.exists(output_path):
            raise FileExistsError(f"Output filename collision: {output_path}")

        # Convert all formats to wav with ffmpeg (quiet, no banner) then fallback
        cmd = [
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-i', file_path,
            '-vn', '-ac', '1', '-ar', '16000', output_path
        ]
        # try ffmpeg first; on any failure, fallback to torchaudio
        try:
            # suppress ffmpeg logs entirely
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            raise FileNotFoundError(
                "ffmpeg 未安裝或不在 PATH，請先安裝 ffmpeg 並確認可執行。"
            )
        except Exception:
            # fallback to torchaudio-based conversion
            try:
                wav, sr = torchaudio.load(file_path)
                if wav.size(0) > 1:
                    wav = wav.mean(dim=0, keepdim=True)
                if sr != 16000:
                    wav = torchaudio.transforms.Resample(sr, 16000)(wav)
                torchaudio.save(output_path, wav, 16000)
            except Exception as e:
                raise RuntimeError(f"ffmpeg 轉檔失敗且 torchaudio 轉檔亦失敗：{e}")

        return temp_file_name
