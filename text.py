import gradio as gr
from utils import encrypt_text, decrypt_text

def process_text(key, text):
    encrypted_text = encrypt_text(key, text)
    decrypted_text = decrypt_text(key, encrypted_text)
    return encrypted_text, decrypted_text

iface = gr.Interface(
    fn=process_text,
    inputs=["text", "text"],
    outputs=["text", "text"],
    title="Text Processing",
    description="Encrypt a text using a key and then decrypt it back."
)

iface.launch()