from abc import ABC, abstractmethod
from modules.utils.config import load_config


class BaseGUI(ABC):
    """
    Abstract base class for GUI apps.
    """
    def __init__(self):
        self.cfg = load_config()

    @abstractmethod
    def run(self):
        """Start the GUI application."""
        pass