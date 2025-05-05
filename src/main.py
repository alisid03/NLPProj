import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from src.chatbot import handle_tool_call
from src.tools import get_all_tools
from src.speech import text_to_speech, speech_to_text
import json


load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()
MODEL = "gpt-4o-mini"


system_message = """
You are a helpful assistant for an airline called FlightAI. You can provide ticket prices, seat availability,
book flights, and retrieve user bookings. Keep your answers short and courteous. Be accurate. If unsure, say you don’t know.
"""

def chat(message, history):
    if(len(history) > 0 and isinstance(history[-1]["content"],gr.File)):
        history.pop()
    file_path = None
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

        # Check tool_responses for file_path
        print(tool_responses)
        if tool_responses:
            for tr in tool_responses:
                try:
                    content_dict = json.loads(tr["content"])
                    if "receipt" in content_dict:
                        file_path = content_dict["receipt"]
                        history.append({"role": "user", "content": message})
                        history.append({"role": "assistant", "content": content_dict["result"]})
                        history.append({"role": "assistant", "content": gr.File(value=file_path)})
                        return "", history
                except Exception as e:
                    print("Failed to parse tool response:", e)
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
        print(assistant_reply)
        if(isinstance(assistant_reply,gr.File)):
            assistant_reply = history[-2]["content"]
        text_to_speech(assistant_reply)

        yield history

    return history

