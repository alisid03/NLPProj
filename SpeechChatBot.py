import os
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import vosk
import pyaudio
import json
from gtts import gTTS
import pygame
from ChatBot import detect_intent, extract_flight_details, get_flights, save_booking, view_booking
import time
from word2number import w2n
import builtins

load_dotenv()

# Initialize NLP tools
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
model = vosk.Model(lang="en-us")
rec = vosk.KaldiRecognizer(model, 16000)

# Speech-to-text function
def speech_to_text():
    import time
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    print("Chatbot: I'm listening. Start speaking, and I'll detect when you're done.")
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
    language = 'en'

    myobj = gTTS(text=text, lang=language, slow=False)

    myobj.save("audio.mp3")

    pygame.mixer.init()

    pygame.mixer.music.load("audio.mp3")

    pygame.mixer.music.play()

    while(pygame.mixer.music.get_busy()):
        time.sleep(0.5)

def speech_chatbot():
    text_to_speech("Welcome to the Speech-Driven Flight Booking Chatbot!")

    while True:
        user_input = speech_to_text()
        if not user_input:
            text_to_speech("I didn't catch that. Can you repeat?")
            continue

        intent = detect_intent(user_input)

        if intent == "exit":
            text_to_speech("Goodbye! Safe travels.")
            break
        elif intent == "view_bookings":
            text_to_speech("Please say your full name to view bookings.")
            name = speech_to_text()
            text_to_speech("Please say your address.")
            address = speech_to_text()
            bookings = view_booking(name, address)
            if bookings:
                for b in bookings:
                    booking_text = f"Booking {b[0]}: from {b[1]} to {b[2]} on {b[3]} with {b[6]} in {b[5]} class."
                    print(booking_text)
                    text_to_speech(booking_text)
            else:
                text_to_speech("No bookings found.")
        elif intent == "search_flight":
            flight_details = extract_flight_details(user_input)
            if flight_details:
                flights = get_flights(flight_details["origin"], flight_details["destination"], flight_details["date_start"], flight_details["date_end"])
                if flights:
                    text_to_speech("Flights found. Would you like to book one?")
                    for f in flights:
                        flight_text = f"Flight {f[0]}: from {f[1]} to {f[2]} on {f[3]} with {f[6]} in {f[5]} class, costing {f[4]} dollars."
                        text_to_speech(flight_text)
                    confirm = speech_to_text().lower()
                    if "yes" in confirm:
                        flight_ids = [f[0] for f in flights]
                        while True:
                            text_to_speech("Please say the flight ID you want to book.")
                            try:
                                chosen = int(w2n.word_to_num((speech_to_text())))
                                print(chosen)
                                if chosen in flight_ids:
                                    text_to_speech("Please say your full name.")
                                    name = speech_to_text()
                                    text_to_speech("Please say your address.")
                                    address = speech_to_text()
                                    save_booking(name, address, next(flight for flight in flights if flight[0] == chosen))
                                    text_to_speech(f"Booking confirmed for flight ID {chosen}.")
                                    break
                                else:
                                    text_to_speech("Invalid ID. Please repeat the flight ID.")
                            except ValueError:
                                text_to_speech("Invalid ID. Please repeat the flight ID.")
                else:
                    text_to_speech("No flights matched your search.")
            else:
                text_to_speech("I couldn't extract flight details. Can you rephrase?")

speech_chatbot()