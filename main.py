import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from chatbot import handle_tool_call
from tools import get_all_tools

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI()
MODEL = "gpt-4o-mini"

system_message = """
You are a helpful assistant for an airline called FlightAI. You can provide ticket prices, seat availability,
book flights, and retrieve user bookings. Keep your answers short and courteous. Be accurate. If unsure, say you don’t know.
"""

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=get_all_tools())

    if response.choices[0].finish_reason == "tool_calls":
        tool_call_msg = response.choices[0].message
        tool_response = handle_tool_call(tool_call_msg)
        messages.append(tool_call_msg)
        messages.append(tool_response)
        response = openai.chat.completions.create(model=MODEL, messages=messages)

    return response.choices[0].message.content

gr.ChatInterface(fn=chat, type="messages").launch()
