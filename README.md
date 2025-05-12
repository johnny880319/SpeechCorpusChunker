# SpeechCorpusChunker
SpeechCorpusChunker is a toolchain for extracting, segmenting, and transcribing audio from long media files or YouTube URLs into a speech-text corpus. It supports both command-line and GUI workflows, with flexible configuration via YAML and dataclass-based type checking.

## Features
- Download and convert YouTube videos or local media (MP4, MP3, WAV)
- Voice activity detection (VAD) using Silero VAD to split speech segments
- Automatic transcription with Faster Whisper (OpenAI Whisper variant)
- Segment-by-segment review and correction via Tkinter or Streamlit GUI
- Organize output into configurable directories with timestamp/UUID subfolders
- Fully configurable via `configs/default.yaml` and dataclasses with type validation

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SpeechCorpusChunker.git
   cd SpeechCorpusChunker
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   ```
3. (Optional) Install additional tools:
   - [ffmpeg](https://ffmpeg.org/) for reliable audio conversion
   - [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloads

## Configuration
All paths and pipeline settings are defined in `configs/default.yaml`. Key sections:
```yaml
paths:
  raw_media_dir: data_storage/raw_media
  converted_wav_dir: temp/converted_wav
  chunked_wav_dir: temp/chunked_wav
  resulted_corpus_dir: data_storage/result/corpus

pipeline:
  sample_rate: 16000
  vad:
    threshold: 0.5
    min_silence_len: 0.3
  asr_model: small
```

## Usage

### Command-Line Interface (CLI)
```bash
python main_cli.py <media_file_or_URL> [more_inputs...]
# Example:
python main_cli.py sample.mp4 https://youtu.be/VIDEO_ID
```

### GUI Interface
- **Tkinter** (desktop):
  ```bash
  python main_gui.py
  ```
- **Streamlit** (web):
  ```bash
  streamlit run modules/gui/streamlit_app.py
  ```

## Dependencies & Licensing
- Python libraries: PyYAML, dacite, torchaudio, soundfile, faster-whisper, torch, yt-dlp
- GUI frameworks: Tkinter (built-in), Streamlit (MIT License)
- External tools: ffmpeg, yt-dlp (both MIT/Free Software)

## License
This project is released under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments
- **Silero VAD** by [snakers4](https://github.com/snakers4/silero-vad) (MIT License)
- **Faster Whisper** by [SYSTRAN](https://github.com/guillaumekln/faster-whisper) (MIT License)
- **Streamlit** (MIT License)
- **yt-dlp** (Unlicense/MIT)
- **FFmpeg** (LGPL/GPL)
