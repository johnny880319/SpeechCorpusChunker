from abc import ABC, abstractmethod

# my module
from modules.utils.config import load_config

class AbstractReader(ABC):
    """
    Abstract base class for all readers.
    """
    def __init__(self):
        """
        Initialize the reader.
        """
        self.cfg = load_config()


    @abstractmethod
    def convert_to_wav(self, *args, **kwargs) -> str:
        """
        Abstract method to convert a file to wav format.
        """
        pass