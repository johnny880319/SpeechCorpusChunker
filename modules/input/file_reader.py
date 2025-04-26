from uuid import uuid4
from datetime import datetime
import time
import os
import subprocess

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

        # Convert all formats to wav with 16kHz sample rate
        subprocess.run([
            'ffmpeg', '-y', '-i', file_path,
            '-ar', '16000', output_path
        ], check=True)

        return temp_file_name
