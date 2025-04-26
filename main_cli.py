import argparse
import os

# my module
from modules.utils.config import load_config
from modules.input.file_reader import FileReader
from modules.input.youtube_reader import YouTubeReader
from modules.segmentation.silero_vad import SileroVAD
from modules.output.audio_exporter import AudioExporter
from modules.transcription.faster_whisper import FasterWhisperASR
from modules.output.transcript_exporter import TranscriptExporter


def main():
    parser = argparse.ArgumentParser(description='Build speech-text corpus from media or URL')
    parser.add_argument('input', nargs='*', default=None, help='Path(s) to media file(s) or YouTube URL(s); if omitted, use files in data_storage_dir')
    args = parser.parse_args()

    cfg = load_config()
    # when no inputs specified, default to all media files in data_storage_dir
    if not args.input:
        data_dir = cfg.paths.raw_media_dir
        try:
            files = [os.path.join(data_dir, f) for f in os.listdir(data_dir)
                     if f.lower().endswith(('.mp4', '.mp3', '.wav'))]
        except FileNotFoundError:
            files = []
        if not files:
            parser.error(f'No input files found in {data_dir}')
        args.input = files

    # initialize components
    file_reader = FileReader()
    yt_reader = YouTubeReader()
    segmenter = SileroVAD(cfg)
    audio_exporter = AudioExporter()
    asr = FasterWhisperASR(cfg)
    transcript_exporter = TranscriptExporter()

    for inp in args.input:
        # get a local media path
        if inp.startswith('http'):
            media_path = yt_reader.download(inp)
        else:
            media_path = inp

        # convert to wav
        wav_name = file_reader.convert_to_wav(media_path)
        wav_path = os.path.join(cfg.paths.converted_wav_dir, wav_name)
        print(f'Converted to WAV: {wav_path}')

        # segment speech
        segments = segmenter.segment(wav_path)
        print(f'Detected {len(segments)} speech segments.')

        # export audio clips
        clip_files = audio_exporter.export(wav_path, segments)
        clip_paths = [os.path.join(cfg.paths.resulted_corpus_dir, f) for f in clip_files]
        print(f'Exported {len(clip_paths)} clips.')

        # transcribe each clip
        transcripts = []
        for index, clip in enumerate(clip_paths):
            text = asr.transcribe(clip)
            transcripts.append(text)
            print(f'Transcribed clip {index + 1}/{len(clip_paths)}: {text}')
        print('Transcription done.')

        # save transcripts
        txt_files = transcript_exporter.export(clip_files, transcripts)
        print(f'Wrote transcripts: {txt_files}')


if __name__ == '__main__':
    main()
