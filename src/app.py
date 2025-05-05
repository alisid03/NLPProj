import gradio as gr
from main import chat, start_speaking, speech_chat, stop_speaking

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

demo.launch(share=True)