import gradio as gr
import os
import soundfile as sf
import numpy as np
import uuid
from utils import encrypt_decrypt_audio

# def process_audio(key, audio_file_path):

#     encrypted_audio = encrypt_decrypt_audio(key, audio_file_path)
#     return encrypted_audio
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


iface = gr.Interface(
    fn=process_audio,
    inputs=["text", "audio"],
    outputs=["audio", "audio"],
    title="Audio Processing",
    description="Encrypt an audio using a key and then decrypt it back."
)
iface.launch()

