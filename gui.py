import tkinter as tk
from tkinter import ttk
from tts_transformers import save_text_to_speech, speakers
import pygame
import os

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Generator")

        ttk.Label(root, text="Enter text (max 200 characters):").pack(pady=10)

        self.text_var = tk.StringVar()
        self.text_text = tk.Text(root, height=5, wrap=tk.WORD, font=('Helvetica', 12))
        self.text_text.pack(pady=10, padx=10)

        self.counter_label = ttk.Label(root, text="")
        self.counter_label.pack(pady=10)

        self.text_text.bind("<<Modified>>", self.update_counter)
        self.schedule_update_counter()

        ttk.Label(root, text="Select speaker:").pack(pady=10)

        speaker_options = ["Scottish Male", "American Male", "American Female", "Canadian Male", "Indian Male", "American Male 2", "American Female 2", "Random"]
        self.speaker_var = tk.StringVar()
        self.speaker_combobox = ttk.Combobox(root, textvariable=self.speaker_var, values=speaker_options)
        self.speaker_combobox.pack(pady=10)
        self.speaker_combobox.set("Random")

        ttk.Button(root, text="Generate Speech", command=self.generate_speech).pack(pady=20)
        ttk.Button(root, text="Play", command=self.play_audio).pack(pady=10)

        self.result_label = ttk.Label(root, text="")
        self.result_label.pack(pady=10)

        pygame.init()

    def generate_speech(self):
        text = self.text_text.get("1.0", tk.END).strip()
        selected_speaker = self.speaker_var.get()

        if selected_speaker == "Random":
            speaker = None
        else:
            speaker_mapping = {
                "Scottish Male": "awb",
                "American Male": "bdl",
                "American Female": "clb",
                "Canadian Male": "jmk",
                "Indian Male": "ksp",
                "American Male 2": "rms",
                "American Female 2": "slt",
                "Random": None
            }
            speaker = speakers[speaker_mapping[selected_speaker]]

        output_filename = save_text_to_speech(text, speaker)
        self.result_label.config(text=f"Speech generated and saved as: {output_filename}")
        self.audio_file = output_filename

    def play_audio(self):
        try:
            if hasattr(self, 'audio_file') and os.path.exists(self.audio_file):
                pygame.mixer.music.load(self.audio_file)
                pygame.mixer.music.play()
                self.result_label.config(text="Playing audio...")
            else:
                self.result_label.config(text="No audio file to play.")
        except Exception as e:
            self.result_label.config(text=f"Error playing audio: {str(e)}")

    def update_counter(self, event=None):
        max_characters = 200
        text_content = self.text_text.get("1.0", tk.END).strip()
        remaining_characters = max_characters - len(text_content)
        self.counter_label.config(text=f"Characters remaining: {remaining_characters}")

    def schedule_update_counter(self):
        self.update_counter()
        self.root.after(100, self.schedule_update_counter)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()

