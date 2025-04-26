import os
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
        :param segment_files: list of wav filenames (not full path)
        :param transcripts: list of corresponding transcript strings
        :return: list of txt filenames
        """
        out_names = []
        for wav_name, text in zip(segment_files, transcripts):
            base, _ = os.path.splitext(wav_name)
            txt_name = f"{base}.txt"
            txt_path = os.path.join(self.output_dir, txt_name)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            out_names.append(txt_name)
        return out_names