import os
from typing import List, Tuple
import torchaudio

from modules.utils.config import load_config


class AudioExporter:
    """
    Export segments of a wav file into separate wav files.
    """
    def __init__(self):
        self.cfg = load_config()
        self.sample_rate = self.cfg.pipeline.sample_rate
        self.output_dir = self.cfg.paths.resulted_corpus_dir

    def export(self, wav_path: str, segments: List[Tuple[float, float]]) -> List[str]:
        """
        Split wav at given time segments and save each as a separate wav file.
        :param wav_path: Path to source wav
        :param segments: List of (start_sec, end_sec)
        :return: List of output filenames
        """
        waveform, sr = torchaudio.load(wav_path)
        if sr != self.sample_rate:
            # resample if needed
            waveform = torchaudio.transforms.Resample(sr, self.sample_rate)(waveform)
            sr = self.sample_rate

        base_name = os.path.splitext(os.path.basename(wav_path))[0]
        out_paths = []  # list of full paths for each segment
        for idx, (start, end) in enumerate(segments):
            start_frame = int(start * sr)
            end_frame = int(end * sr)
            segment_wave = waveform[:, start_frame:end_frame]
            out_filename = f"{base_name}_{idx:03d}.wav"
            out_path = os.path.join(self.output_dir, out_filename)
            torchaudio.save(out_path, segment_wave, sr)
            out_paths.append(out_path)
        return out_paths
