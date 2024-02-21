from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import random
import string
import soundfile as sf

# Verificăm disponibilitatea dispozitivului CUDA (GPU) pentru accelerarea procesării,
# altfel utilizăm CPU.
device = "cuda" if torch.cuda.is_available() else "cpu"

# Încărcăm procesorul (processor) pentru modelul SpeechT5.
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")

# Încărcăm modelul SpeechT5ForTextToSpeech și îl mutăm pe dispozitivul specificat.
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)

# Încărcăm modelul SpeechT5HifiGan pentru vocoder și îl mutăm pe dispozitivul specificat.
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(device)

# Încărcăm setul de date cu înglobări (embeddings) ale vorbitorilor pentru
# a obține caracteristicile vocale.
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")

# Dicționar cu identificatori pentru vorbitorii utilizați.
speakers = {
    'awb': 0,     # Bărbat scoțian
    'bdl': 1138,  # Bărbat american
    'clb': 2271,  # Femeie americană
    'jmk': 3403,  # Bărbat canadian
    'ksp': 4535,  # Bărbat indian
    'rms': 5667,  # Bărbat american
    'slt': 6799   # Femeie americană
}

def save_text_to_speech(text, speaker=None):
    # Prelucrăm textul pentru a-l transforma în input pentru modelul SpeechT5.
    inputs = processor(text=text, return_tensors="pt").to(device)

    # Dacă avem un vorbitor specificat, încărcăm înglobările (embeddings) corespunzătoare.
    if speaker is not None:
        speaker_embeddings = torch.tensor(embeddings_dataset[speaker]["xvector"]).unsqueeze(0).to(device)
    else:
        # Dacă nu avem un vorbitor specificat, generăm un vector aleatoriu, reprezentând o voce aleatoare.
        speaker_embeddings = torch.randn((1, 512)).to(device)

    # Generăm discursul utilizând modelele SpeechT5 și vocoderul.
    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

    # Construim un nume de fișier în funcție de prezența sau absența unui vorbitor specificat.
    if speaker is not None:
        output_filename = f"{speaker}-{'-'.join(text.split()[:6])}.mp3"
    else:
        random_str = ''.join(random.sample(string.ascii_letters+string.digits, k=5))
        output_filename = f"{random_str}-{'-'.join(text.split()[:6])}.mp3"

    # Salvăm discursul generat într-un fișier cu o rată de eșantionare de 16KHz.
    sf.write(output_filename, speech.cpu().numpy(), samplerate=16000)

    # Returnăm numele fișierului pentru referință.
    return output_filename

# Generăm discurs cu voce feminină americană.
save_text_to_speech("Python is my favorite programming language", speaker=speakers["slt"])

# Generăm discurs cu o voce aleatoare.
save_text_to_speech("Python is my favorite programming language")

# Text de test care să fie generat pentru toți vorbitorii.
text = """In his miracle year, he published four groundbreaking papers. 
These outlined the theory of the photoelectric effect, explained Brownian motion, 
introduced special relativity, and demonstrated mass-energy equivalence."""

# Generăm discurs pentru fiecare vorbitor și salvăm în fișiere separate.
for speaker_name, speaker in speakers.items():
    output_filename = save_text_to_speech(text, speaker)
    print(f"Salvat {output_filename}")

# Generăm discurs cu o voce aleatoare.
output_filename = save_text_to_speech(text)
print(f"Salvat {output_filename}")
