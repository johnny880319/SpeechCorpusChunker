from dataclasses import dataclass

@dataclass(frozen=True)
class PathsConfig:
    temp_dir: str
    converted_wav_dir: str
    chunked_wav_dir: str  # new: VAD chunk output directory
    data_storage_dir: str
    raw_media_dir: str
    resulted_corpus_dir: str

@dataclass(frozen=True)
class VADConfig:
    threshold: float
    min_silence_len: float  # seconds

@dataclass(frozen=True)
class PipelineConfig:
    sample_rate: int
    vad: VADConfig
    asr_model: str

@dataclass
class AppConfig:
    """
    Coincide with the default.yaml structure.
    """
    paths: PathsConfig
    pipeline: PipelineConfig