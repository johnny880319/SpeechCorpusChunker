import os
import shutil
from typing import List
from modules.utils.config import load_config


class TranscriptExporter:
    """
    Export ASR transcripts to text files.
    """
    def __init__(self):
        cfg = load_config()
        self.output_dir = cfg.paths.resulted_corpus_dir

    def export(self, segment_files: List[str], transcripts: List[str]) -> List[str]:
        """
        Write each transcript to a .txt file named after the segment wav.
        :param segment_files: list of full wav file paths
        :param transcripts: list of corresponding transcript strings
        :return: list of txt full paths
        """
        out_paths = []
        for wav_path, text in zip(segment_files, transcripts):
            # derive nested folder: timestamp/uuid
            fname = os.path.basename(wav_path)
            parts = fname.split('_')  # [timestamp, uuid, idx.wav]
            if len(parts) < 3:
                subdir = self.output_dir
            else:
                timestamp, uid = parts[0], parts[1]
                subdir = os.path.join(self.output_dir, timestamp, uid)
                os.makedirs(subdir, exist_ok=True)
            # copy wav file
            shutil.copy2(wav_path, subdir)
            # write txt alongside
            base, _ = os.path.splitext(fname)
            txt_name = f"{base}.txt"
            txt_path = os.path.join(subdir, txt_name)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            out_paths.append(txt_path)
        return out_paths