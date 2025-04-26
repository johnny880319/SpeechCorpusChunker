from abc import ABC, abstractmethod


class AbstractASR(ABC):
    """
    Abstract base class for ASR transcription.
    """
    def __init__(self, cfg):
        self.cfg = cfg

    @abstractmethod
    def transcribe(self, wav_path: str) -> str:
        """
        Transcribe a wav file and return the transcript string.
        """
        pass