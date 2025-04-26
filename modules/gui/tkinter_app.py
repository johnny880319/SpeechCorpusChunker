import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import os

from .base_gui import BaseGUI
from modules.input.file_reader import FileReader
from modules.input.youtube_reader import YouTubeReader
from modules.segmentation.silero_vad import SileroVAD
from modules.output.audio_exporter import AudioExporter
from modules.transcription.faster_whisper import FasterWhisperASR
from modules.output.transcript_exporter import TranscriptExporter
from modules.utils.config import load_config


class TkinterApp(BaseGUI):
    def __init__(self):
        super().__init__()
        self.root = tk.Tk()
        self.root.title('Speech Corpus Builder')
        # Input field
        tk.Label(self.root, text='File path or YouTube URL:').pack(padx=5, pady=5)
        self.entry = tk.Entry(self.root, width=60)
        self.entry.pack(padx=5, pady=5)
        tk.Button(self.root, text='Browse File', command=self.browse_file).pack(padx=5, pady=5)
        tk.Button(self.root, text='Start', command=self.start).pack(padx=5, pady=5)
        # Log area
        self.log = scrolledtext.ScrolledText(self.root, height=20)
        self.log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[('Media files', '*.wav *.mp3 *.mp4'), ('All files', '*.*')])
        if path:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, path)

    def start(self):
        t = threading.Thread(target=self.run_pipeline, daemon=True)
        t.start()

    def run_pipeline(self):
        inp = self.entry.get().strip()
        if not inp:
            messagebox.showwarning('Warning', 'Please enter a file path or URL.')
            return
        cfg = load_config()
        fr = FileReader()
        yt = YouTubeReader()
        seg = SileroVAD(cfg)
        exp_audio = AudioExporter()
        asr = FasterWhisperASR(cfg)
        exp_txt = TranscriptExporter()
        # read or download
        self.log.insert(tk.END, f'Processing {inp}\n')
        self.log.see(tk.END)
        try:
            media = yt.download(inp) if inp.startswith('http') else inp
            self.log.insert(tk.END, f'Media path: {media}\n')
            wav = fr.convert_to_wav(media)
            wav_path = os.path.join(cfg.paths.converted_wav_dir, wav)
            self.log.insert(tk.END, f'WAV: {wav_path}\n')
            segs = seg.segment(wav_path)
            self.log.insert(tk.END, f'Segments: {len(segs)}\n')
            clips = exp_audio.export(wav_path, segs)
            self.log.insert(tk.END, f'Clips: {len(clips)}\n')
            transcripts = [asr.transcribe(os.path.join(cfg.paths.temp_dir, c)) for c in clips]
            self.log.insert(tk.END, 'Transcribed clips\n')
            txts = exp_txt.export(clips, transcripts)
            self.log.insert(tk.END, f'TXT files: {txts}\nDone.\n')
        except Exception as e:
            self.log.insert(tk.END, f'Error: {e}\n')
        self.log.see(tk.END)

    def run(self):
        self.root.mainloop()