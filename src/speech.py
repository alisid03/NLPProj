import pyaudio
import time
import threading
from gtts import gTTS
import pygame
import vosk
import json
import re

model = vosk.Model(lang="en-us")
rec = vosk.KaldiRecognizer(model, 16000)


def speech_to_text():
    import time
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    text = ""
    silence_threshold = 1.5  # seconds of silence
    last_spoken = time.time()
    stream.start_stream()

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            recognized_text = result.get('text', '').strip()
            if recognized_text:
                print("You: " + recognized_text)
                text += " " + recognized_text
                last_spoken = time.time()
        else:
            # Check for silence
            if time.time() - last_spoken > silence_threshold and text:
                print("Chatbot: Got it! Let's continue.")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()
    return text.strip()

def text_to_speech(text):
    print(f"Chatbot: {text}")

    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)

    language = 'en'

    myobj = gTTS(text=text, lang=language, slow=False)

    myobj.save("data/audio.mp3")

    pygame.mixer.init()

    pygame.mixer.music.load("data/audio.mp3")

    pygame.mixer.music.play()

    while(pygame.mixer.music.get_busy()):
        time.sleep(0.5)