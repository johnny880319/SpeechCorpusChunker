import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import os
import winsound
from concurrent.futures import ThreadPoolExecutor
import shutil

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
        self.log = scrolledtext.ScrolledText(self.root, height=10)
        self.log.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        # Editor area for segment-by-segment review
        self.editor_frame = tk.Frame(self.root)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
            # clear old segment files
            temp_dir = self.cfg.paths.temp_dir
            for fname in os.listdir(temp_dir):
                path = os.path.join(temp_dir, fname)
                if os.path.isfile(path) and fname.lower().endswith('.wav'):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
            clips = exp_audio.export(wav_path, segs)
            self.log.insert(tk.END, f'Clips: {len(clips)}\n')
            # prepare for background transcription
            self.clips = clips
            self.transcripts = [None] * len(clips)
            # transcribe first clip synchronously for quick UI
            self.transcripts[0] = asr.transcribe(clips[0])
            # start background workers for remaining clips
            self.executor = ThreadPoolExecutor(max_workers=min(4, len(clips)))
            for i in range(1, len(clips)):
                self.executor.submit(self._bg_transcribe, i, clips[i], asr)
            self.current = 0
            # render first segment editor
            self.root.after(0, self._render_segment)
        except Exception as e:
            self.log.insert(tk.END, f'Error: {e}\n')
        self.log.see(tk.END)

    def _bg_transcribe(self, idx, clip_path, asr):
        try:
            text = asr.transcribe(clip_path)
        except Exception as e:
            text = f'[Error: {e}]'
        self.transcripts[idx] = text

    def _play_clip(self):
        # clip paths are full paths
        path = self.clips[self.current]
        winsound.PlaySound(path, winsound.SND_FILENAME)

    def _save_next(self):
        # save edited transcript and corresponding wav to nested folder
        text = self.text_widget.get('1.0', tk.END).strip()
        clip_path = self.clips[self.current]
        name = os.path.basename(clip_path)
        parts = name.split('_')
        # determine subdirectory based on timestamp and uuid
        if len(parts) >= 3:
            timestamp, uid = parts[0], parts[1]
            subdir = os.path.join(self.cfg.paths.resulted_corpus_dir, timestamp, uid)
        else:
            subdir = self.cfg.paths.resulted_corpus_dir
        os.makedirs(subdir, exist_ok=True)
        # copy wav file into subdir
        shutil.copy2(clip_path, subdir)
        # write transcript
        base, _ = os.path.splitext(name)
        txt_path = os.path.join(subdir, f'{base}.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        self.log.insert(tk.END, f'已儲存至: {subdir}\n')
        self.log.see(tk.END)
        # go next or finish
        if self.current < len(self.clips) - 1:
            self.current += 1
            self._render_segment()
        else:
            messagebox.showinfo('Done', 'All segments saved.')

    def _prev(self):
        if self.current > 0:
            self.current -= 1
            self._render_segment()

    def _render_segment(self):
        # clear editor area
        for w in self.editor_frame.winfo_children():
            w.destroy()
        idx = self.current
        total = len(self.clips)
        tk.Label(self.editor_frame, text=f'Segment {idx+1}/{total}').pack(padx=5, pady=5)
        tk.Button(self.editor_frame, text='Play', command=self._play_clip).pack(padx=5, pady=5)
        # text area: show placeholder until transcript ready
        self.text_widget = scrolledtext.ScrolledText(self.editor_frame, height=8)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        btn_frame = tk.Frame(self.editor_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text='Previous', command=self._prev).pack(side=tk.LEFT, padx=5)
        self.save_btn = tk.Button(btn_frame, text='Save & Next', command=self._save_next)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        # start polling for transcript readiness now that save_btn exists
        self._update_text_area()

    def _update_text_area(self):
        # check if transcript available
        idx = self.current
        txt = self.transcripts[idx]
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        if txt is None:
            self.text_widget.insert('1.0', 'Transcribing...')
            self.save_btn.config(state='disabled')
            # poll again after 500ms
            self.root.after(500, self._update_text_area)
        else:
            self.text_widget.insert('1.0', txt)
            self.save_btn.config(state='normal')
        self.text_widget.config(state='normal')

    def run(self):
        self.root.mainloop()