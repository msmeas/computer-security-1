import gradio as gr
from utils import encrypt_decrypt_image


def process_image(key, image):
    encrypted_image = encrypt_decrypt_image(key, image)
    # decrypted_image = encrypt_decrypt_image(key, encrypted_image)
    return encrypted_image


iface = gr.Interface(
    fn=process_image,
    inputs=["text", "image"],
    outputs=["image", "image"],
    title="Image Processing",
    description="Encrypt an image using a key and then decrypt it back."
) 
iface.launch()