import streamlit as st
import os
import tempfile

from .base_gui import BaseGUI
from modules.input.file_reader import FileReader
from modules.input.youtube_reader import YouTubeReader
from modules.segmentation.silero_vad import SileroVAD
from modules.output.audio_exporter import AudioExporter
from modules.transcription.faster_whisper import FasterWhisperASR
from modules.output.transcript_exporter import TranscriptExporter
from modules.utils.config import load_config


class StreamlitApp(BaseGUI):
    def run(self):
        st.title('Speech Corpus Builder')
        cfg = load_config()
        file_reader = FileReader()
        yt_reader = YouTubeReader()
        segmenter = SileroVAD(cfg)
        audio_exporter = AudioExporter()
        asr = FasterWhisperASR(cfg)
        transcript_exporter = TranscriptExporter()

        st.subheader('Input')
        url = st.text_input('YouTube URL')
        upload = st.file_uploader('Or upload media file', type=['wav', 'mp3', 'mp4'])

        if st.button('Start'):
            st.write('Processing...')
            if url:
                media_path = yt_reader.download(url)
            elif upload is not None:
                fd, path = tempfile.mkstemp(suffix=os.path.splitext(upload.name)[1])
                with os.fdopen(fd, 'wb') as f:
                    f.write(upload.read())
                media_path = path
            else:
                st.error('Please provide a URL or upload a file.')
                return

            st.write(f'Media path: {media_path}')
            wav_name = file_reader.convert_to_wav(media_path)
            wav_path = os.path.join(cfg.paths.converted_wav_dir, wav_name)
            st.write(f'Converted to WAV: {wav_path}')

            segments = segmenter.segment(wav_path)
            st.write(f'Detected {len(segments)} speech segments')

            clips = audio_exporter.export(wav_path, segments)
            st.write(f'Exported {len(clips)} clips')

            transcripts = []
            for clip in clips:
                clip_path = os.path.join(cfg.paths.temp_dir, clip)
                text = asr.transcribe(clip_path)
                transcripts.append(text)
            st.write('Transcription complete')

            txts = transcript_exporter.export(clips, transcripts)
            st.write('Generated transcripts:')
            for txt in txts:
                st.write(txt)
