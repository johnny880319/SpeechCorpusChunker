from faster_whisper import WhisperModel

from .base_asr import AbstractASR


class FasterWhisperASR(AbstractASR):
    """
    ASR implementation using Faster Whisper.
    """
    def __init__(self, cfg):
        super().__init__(cfg)
        # Load model; cfg.pipeline.asr_model may be model name or path
        self.model = WhisperModel(
            model_size_or_path=self.cfg.pipeline.asr_model,
            device='auto',
            compute_type='int8'
        )

    def transcribe(self, wav_path: str) -> str:
        """
        Transcribe the audio file and return the concatenated transcript.
        """
        segments, _ = self.model.transcribe(
            wav_path,
            beam_size=5,
            word_timestamps=False
        )
        # segments is a list of Segment objects with `.text` attribute
        transcript = ''.join([seg.text for seg in segments])
        return transcript
