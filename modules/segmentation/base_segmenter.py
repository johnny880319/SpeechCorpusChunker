from abc import ABC, abstractmethod
from typing import List, Tuple


class AbstractSegmenter(ABC):
    """
    Abstract base class for audio segmentation (VAD).
    """
    def __init__(self, cfg):
        """Store configuration with sample rate and VAD params"""
        self.cfg = cfg

    @abstractmethod
    def segment(self, wav_path: str) -> List[Tuple[float, float]]:
        """
        Segment audio into speech regions.
        :param wav_path: Path to input wav file.
        :return: List of (start_sec, end_sec) tuples representing speech segments.
        """
        pass
