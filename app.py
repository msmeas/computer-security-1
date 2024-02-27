import gradio as gr
import os
import soundfile as sf
import uuid
import numpy as np
from utils import key_generator, encrypt_text, decrypt_text, encrypt_decrypt_image, encrypt_decrypt_video, encrypt_decrypt_audio


def process_key(length16key):
    if len(length16key) == 16:
        c1prime, c2prime = key_generator(length16key)
        return c1prime, c2prime, "Key submitted!"
    else:
        return None, None, "Key must be 16 characters long."


def process_text(key, text):
    encrypted_text = encrypt_text(key, text)
    decrypted_text = decrypt_text(key, encrypted_text)
    return encrypted_text, decrypted_text


def process_video(key, video):
    encrypted_video = encrypt_decrypt_video(key, video)
    # decrypted_video = encrypt_decrypt_video(key, encrypted_video)
    return encrypted_video


def process_image(key, image):
    image_array = np.array(image)
    encrypted_image_tuple = encrypt_decrypt_image(key, image_array)
    encrypted_image = encrypted_image_tuple[0]  # adjust this index based on where the image is in the tuple
    # decrypted_image = encrypt_decrypt_image(key, encrypted_image)
    return encrypted_image


def process_audio(key, audio_input):
    # Unpack audio_input into samplerate and audio_data
    samplerate, audio_data = audio_input

    # Convert to numpy array if it's not already
    if not isinstance(audio_data, np.ndarray):
        audio_data = np.array(audio_data)

    # Create a file path for the uploaded audio
    audio_file_path = "audios/uploaded/audio_" + str(uuid.uuid4()) + ".wav"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)

    # Save the audio data to the file
    sf.write(audio_file_path, audio_data, samplerate)

    # Pass the file path to encrypt_decrypt_audio
    encrypted_audio = encrypt_decrypt_audio(key, audio_file_path)

    # Convert to numpy array if it's a list
    if isinstance(encrypted_audio, list):
        encrypted_audio = np.array(encrypted_audio)

    # Create a file path for the encrypted audio
    encrypted_audio_file_path = "audios/encrypted/audio_" + str(uuid.uuid4()) + ".wav"

    # Save the encrypted audio data to a new file
    sf.write(encrypted_audio_file_path, encrypted_audio, samplerate)

    # Delete the uploaded audio file when you're done
    os.remove(audio_file_path)

    # Return the path to the encrypted audio file
    return encrypted_audio_file_path


with gr.Blocks() as app:
    gr.Markdown("#### Enter a 16-character key for encryption:")
    length16key = gr.Textbox(label="Key")
    submit_button = gr.Button("Submit")
    output_c1prime = gr.Textbox(label="c1prime", lines=1, interactive=False)
    output_c2prime = gr.Textbox(label="c2prime", lines=1, interactive=False)
    output_message = gr.Textbox(label="Output", lines=1, interactive=False)
    with gr.Accordion("Text"):
        gr.Markdown("#### Text Encryption")
        text_input = gr.Textbox(label="Text")
        text_output = gr.Textbox(label="Encrypted Text", lines=5, interactive=False)
        text_decrypted_output = gr.Textbox(label="Decrypted Text", lines=5, interactive=False)
        text_submit_button = gr.Button("Submit")
        text_submit_button.click(
            fn=process_text,
            inputs=[length16key, text_input],
            outputs=[text_output, text_decrypted_output]
        )
    with gr.Accordion("Video"):
        gr.Markdown("#### Video Encryption")
        video_input = gr.Video(label="Video")
        video_output = gr.Video(label="Encrypted Video")
        video_submit_button = gr.Button("Submit")
        video_submit_button.click(
            fn=process_video,
            inputs=[length16key, video_input],
            outputs=[video_output]
        )
    with gr.Accordion("Image"):
        gr.Markdown("#### Image Encryption")
        image_input = gr.Image(label="Image", type="pil")
        image_output = gr.Image(label="Encrypted Image", type="pil", interactive=False)
        image_submit_button = gr.Button("Encrypt Image")
        image_submit_button.click(
            fn=process_image,
            inputs=[length16key, image_input],
            outputs=image_output
        )

    with gr.Accordion("Audio"):
        gr.Markdown("#### Audio Encryption")
        audio_input = gr.Audio(label="Audio")
        audio_output = gr.Audio(label="Encrypted Audio")
        audio_submit_button = gr.Button("Submit")
        audio_submit_button.click(
            fn=process_audio,
            inputs=[length16key, audio_input],
            outputs=[audio_output]
        )
    submit_button.click(
        fn=process_key,
        inputs=length16key,
        outputs=[output_c1prime, output_c2prime, output_message]
    )

app.launch()
