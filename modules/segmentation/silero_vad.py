import torch
import soundfile as sf
import torchaudio

from .base_segmenter import AbstractSegmenter


class SileroVAD(AbstractSegmenter):
    """
    Silero VAD implementation.
    """
    def __init__(self, cfg):
        super().__init__(cfg)
        # Load model and utils from snakers4 silero-vad, using standard get_speech_timestamps
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        # utils[0] is always get_speech_timestamps (non-adaptive)
        self.get_speech_ts = utils[0]

    def segment(self, wav_path: str):
        """
        Segment wav into speech regions using Silero VAD.
        Returns list of (start_sec, end_sec).
        """
        # load and resample audio manually
        data, orig_sr = sf.read(wav_path)
        # mono
        if data.ndim > 1:
            data = data.mean(axis=1)
        # to torch tensor (channel-first)
        audio = torch.from_numpy(data).float().unsqueeze(0)
        target_sr = self.cfg.pipeline.sample_rate
        if orig_sr != target_sr:
            audio = torchaudio.functional.resample(audio, orig_sr, target_sr)
        # collapse to 1D
        audio = audio.squeeze(0)

        # run VAD: use non-adaptive get_speech_timestamps
        segments = self.get_speech_ts(
            audio,
            self.model,
            threshold=self.cfg.pipeline.vad.threshold,
            sampling_rate=target_sr
        )
        # segments is list of dict with 'start' and 'end' keys (in samples)
        out = [
            (seg['start'] / self.cfg.pipeline.sample_rate,
             seg['end'] / self.cfg.pipeline.sample_rate)
            for seg in segments
        ]
        return out
