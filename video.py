import gradio as gr
from utils import encrypt_decrypt_video


def process_video(key, video):
    encrypted_video = encrypt_decrypt_video(key, video)
    # decrypted_video = encrypt_decrypt_video(key, encrypted_video)
    return encrypted_video


iface = gr.Interface(
    fn=process_video,
    inputs=["text", "video"],
    outputs=["video"],
    title="Video Processing",
    description="Encrypt a video using a key and then decrypt it back."
)
iface.launch()