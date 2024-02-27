import math
import numpy as np
import cv2
import uuid
import soundfile as sf


c1 = -0.5
c2 = 0.1
y1 = 0.481
y2 = -0.133


def key_generator(length16key):
    y_array = []
    temp = ord(length16key[0]) + c1 * y1 + c2 * y2
    y_array.append(math.fmod(temp+1, 2.0) - 1)

    temp = ord(length16key[1]) + c1 * y_array[0] + c2 * y1
    y_array.append(math.fmod(temp+1, 2.0) - 1)

    for i in range(2, 16):
        temp = ord(length16key[i]) + c1 * y_array[i - 1] + c2 * y_array[i - 2]
        y_array.append(math.fmod(temp+1, 2.0) - 1)

    for i in range(16):
        if i == 14:
            print("c1prime: " + str(y_array[i]))
        elif i == 15:
            print("c2prime: " + str(y_array[i]))
        else:
            print(str(y_array[i]))
    c1prime = y_array[14]
    c2prime = y_array[15]
    return c1prime, c2prime


def f(x: float) -> float:
    return ((x + 1) % 2) - 1


def normalized(value):
    return value / 128.0


def denormalized(value):
    return np.round(value * 128.0).astype(np.uint8)


def encrypt_value(value, y1, y2, c1prime, c2prime):
    return f(value + c1prime * y1 + c2prime * y2)


def decrypt_value(value, y1, y2, c1prime, c2prime):
    return f(value - c1prime * y1 - c2prime * y2)


def encryptor(key, original_values):
    normalized_original_values = [normalized(value) for value in original_values]
    encrypted_values = []
    denormalized_encrypted_values = []
    c1prime, c2prime = key_generator(key)

    temp_encrypted_value = encrypt_value(normalized_original_values[0], y1, y2, c1prime, c2prime)
    temp_denormalized_encrypted_value = normalized(denormalized(temp_encrypted_value)) # NORMALIZED_CEPTION
    encrypted_values.append(temp_denormalized_encrypted_value)

    temp_encrypted_value = encrypt_value(normalized_original_values[1], encrypted_values[0], y1, c1prime, c2prime)
    temp_denormalized_encrypted_value = normalized(denormalized(temp_encrypted_value)) # NORMALIZED_CEPTION
    encrypted_values.append(temp_denormalized_encrypted_value)

    for i in range(2, len(normalized_original_values)):
        temp_encrypted_value = encrypt_value(normalized_original_values[i], encrypted_values[i - 1], encrypted_values[i - 2], c1prime, c2prime)
        temp_denormalized_encrypted_value = normalized(denormalized(temp_encrypted_value)) # NORMALIZED_CEPTION
        encrypted_values.append(temp_denormalized_encrypted_value)
    
    denormalized_encrypted_values = [denormalized(value) for value in encrypted_values]

    return denormalized_encrypted_values


def decryptor(key, encrypted_values):
    normalized_encrypted_values = [normalized(value) for value in encrypted_values]
    decrypted_values = []
    c1prime, c2prime = key_generator(key)

    decrypted_values.append(decrypt_value(normalized_encrypted_values[0], y1, y2, c1prime, c2prime))

    decrypted_values.append(decrypt_value(normalized_encrypted_values[1], normalized_encrypted_values[0], y1, c1prime, c2prime))

    for i in range(2, len(normalized_encrypted_values)):
        decrypted_values.append(decrypt_value(normalized_encrypted_values[i], normalized_encrypted_values[i - 1], normalized_encrypted_values[i - 2], c1prime, c2prime))

    denormalized_decrypted_values = [denormalized(value) for value in decrypted_values]

    return denormalized_decrypted_values


# Encrypt function for text
def encrypt_text(key, original_text):
    c1prime, c2prime = key_generator(key)
    encrypted_values = []
    for char in original_text:
        value = ord(char)  # Convert character to ASCII value
        norm_value = normalized(value)  # Normalize ASCII value to [-1, 1]
        encrypted_val = encrypt_value(norm_value, y1, y2, c1prime, c2prime)  # Encrypt normalized value
        encrypted_values.append(denormalized(encrypted_val))  # Denormalize and append
    # Convert encrypted values back to characters
    encrypted_text = ''.join(chr(val % 128) for val in encrypted_values)
    return encrypted_text

# Decrypt function for text
def decrypt_text(key, encrypted_text):
    c1prime, c2prime = key_generator(key)  # Recalculate key-dependent parameters.
    decrypted_values = []
    for char in encrypted_text:
        value = ord(char)  # Convert character to ASCII value
        norm_value = normalized(value)  # Normalize ASCII value to [-1, 1]
        decrypted_val = decrypt_value(norm_value, y1, y2, c1prime, c2prime)  # Decrypt normalized value
        decrypted_values.append(denormalized(decrypted_val))  # Denormalize and append
    # Convert decrypted values back to characters
    decrypted_text = ''.join(chr(val % 128) for val in decrypted_values)
    return decrypted_text


def encrypt_decrypt_image(key, original_image):

    if original_image is None:
        print("Error: Unable to load the image.")
        return None

    # Reshape the image array to a one-dimensional array
    gray_scale = original_image if len(original_image.shape) == 2 else cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    flattened_image = gray_scale.ravel()

    # Encrypt the flattened image
    flattened_encrypted_image = encryptor(key, flattened_image)
    encrypted_image = np.reshape(flattened_encrypted_image, gray_scale.shape)

    # Save the encrypted image
    encrypted_image_path = "images/encrypted/image_" + str(uuid.uuid4()) + ".jpg"
    cv2.imwrite(encrypted_image_path, encrypted_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    # Decrypt the encrypted image
    decrypted_image = decryptor(key, flattened_encrypted_image)
    decrypted_image = np.reshape(decrypted_image, gray_scale.shape)

    # Save the decrypted image
    decrypted_image_path = "images/decrypted/image_" + str(uuid.uuid4()) + ".jpg"
    cv2.imwrite(decrypted_image_path, decrypted_image)

    return encrypted_image_path, decrypted_image_path


def encrypt_decrypt_video(key, video_path):
    cap = cv2.VideoCapture(video_path)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    encrypted_video_path = "videos/encrypted/video_" + str(uuid.uuid4()) + ".mp4"
    outEncrypted = cv2.VideoWriter(encrypted_video_path, fourcc, fps, (width, height))
    decrypted_video_path = "videos/decrypted/video_" + str(uuid.uuid4()) + ".mp4"
    outDecrypted = cv2.VideoWriter(decrypted_video_path, fourcc, fps, (width, height))

    for _ in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        encrypted_frame, decrypted_frame = encrypt_decrypt_image(key, frame)

        outEncrypted.write(cv2.imread(encrypted_frame))
        outDecrypted.write(cv2.imread(decrypted_frame))

    cap.release()
    outEncrypted.release()
    outDecrypted.release()


def encrypt_decrypt_audio(key, audio_file_path):
    # Read the audio file using soundfile
    audio, samplerate = sf.read(audio_file_path)

    encrypted_audio = encryptor(key, audio)

    encrypted_audio_path = "audios/encrypted/audio_" + str(uuid.uuid4()) + ".wav"
    encrypted_audio = np.array(encrypted_audio).astype(np.int16)  # Convert to numpy array before calling astype
    sf.write(encrypted_audio_path, encrypted_audio, samplerate)

    decrypted_audio = decryptor(key, encrypted_audio)
    decrypted_audio = np.array(decrypted_audio).astype(np.int16)  # Convert to numpy array before calling astype

    decrypted_audio_path = "audios/decrypted/audio_" + str(uuid.uuid4()) + ".wav"
    sf.write(decrypted_audio_path, decrypted_audio, samplerate)

    # Print the result
    print("Original Length Audio", len(audio))
    print("Encrypted Length Audio", len(encrypted_audio))
    print("Decrypted Length Audio", len(decrypted_audio))
    return encrypted_audio, decrypted_audio
