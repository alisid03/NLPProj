import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from ChatBot import handle_tool_call
from tools import get_all_tools
import vosk
from gtts import gTTS
import pygame
import json
import pyaudio
import time
import threading

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

    return "", history

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

is_speaking = False  # Global flag

def start_speaking(history):
    global is_speaking
    is_speaking = True
    return "", history  # no immediate updates

def stop_speaking():
    global is_speaking
    is_speaking = False

def speech_chat(history: list):
    global is_speaking

    while is_speaking:
        user_message = speech_to_text()
        text_to_speech("Gotcha")

        if not user_message.strip():
            continue

        if user_message.lower() in ["stop", "exit", "quit"]:
            is_speaking = False
            EXIT_MESSAGE = "exiting speech mode"
            text_to_speech(EXIT_MESSAGE)
            break

        _, history = chat(user_message, history)

        assistant_reply = history[-1]["content"]
        text_to_speech(assistant_reply)

        yield history

    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    with gr.Row():
        textbox = gr.Textbox(placeholder="Type your message here...")
        send_btn = gr.Button("Send")
        speech_start_btn = gr.Button("🎤 Start Speaking")
        speech_stop_btn = gr.Button("🛑 Say 'exit' to exit speech mode")

    # Text input path
    textbox.submit(fn=chat, inputs=[textbox, chatbot], outputs=[textbox, chatbot])
    send_btn.click(fn=chat, inputs=[textbox, chatbot], outputs=[textbox, chatbot])

    # Speech input path
    speech_start_btn.click(fn=start_speaking, inputs=chatbot, outputs=[textbox, chatbot], queue=False).then(
        fn=speech_chat, inputs=chatbot, outputs=chatbot
    )
    speech_stop_btn.click(fn=stop_speaking, inputs=None, outputs=None)

demo.launch()