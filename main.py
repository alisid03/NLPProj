import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from chatbot import handle_tool_call
from tools import get_all_tools
import vosk
from gtts import gTTS
import pygame
import json
import pyaudio
import time

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()
MODEL = "gpt-4o-mini"

model = vosk.Model(lang="en-us")
rec = vosk.KaldiRecognizer(model, 16000)

system_message = """
You are a helpful assistant for an airline called FlightAI. You can provide ticket prices, seat availability,
book flights, and retrieve user bookings. Keep your answers short and courteous. Be accurate. If unsure, say you don’t know.
"""

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=get_all_tools())

    print(f"\nInput: {message}")

    if response.choices[0].finish_reason == "tool_calls":
        tool_call_msg = response.choices[0].message

        # Handle ALL tool calls
        tool_responses = []
        for single_tool_call in tool_call_msg.tool_calls:
            tool_response = handle_tool_call(single_tool_call)  # <<< modified
            tool_responses.append(tool_response)

        # Append the tool call request
        messages.append(tool_call_msg)

        # Append all tool responses
        messages.extend(tool_responses)

        # Now re-call OpenAI with updated messages
        response = openai.chat.completions.create(model=MODEL, messages=messages)

    final_assistant_message = response.choices[0].message

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": final_assistant_message.content})

    return history

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
    language = 'en'

    myobj = gTTS(text=text, lang=language, slow=False)

    myobj.save("audio.mp3")

    pygame.mixer.init()

    pygame.mixer.music.load("audio.mp3")

    pygame.mixer.music.play()

    while(pygame.mixer.music.get_busy()):
        time.sleep(0.5)

def speech_chat(history):
    message = speech_to_text()
    history = chat(message, history)
    assistant_reply = history[-1]["content"]  # Get the assistant's latest reply
    text_to_speech(assistant_reply)
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    with gr.Row():
        textbox = gr.Textbox(placeholder="Type your message here...")
        send_btn = gr.Button("Send")
        speech_btn = gr.Button("🎤 Speak")

    # Text input handling
    send_btn.click(fn=chat, inputs=[textbox, chatbot], outputs=chatbot)
    
    # Speech input handling
    speech_btn.click(fn=speech_chat, inputs=chatbot, outputs=chatbot)

demo.launch()