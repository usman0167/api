# import os
# import deepspeech
# import numpy as np
# import wave
# from flask import Flask, request, jsonify
# from pydub import AudioSegment

# # Initialize Flask App
# app = Flask(__name__)

# # Paths to DeepSpeech model and scorer
# MODEL_PATH = "deepspeech-0.9.3-models.pbmm"
# SCORER_PATH = "deepspeech-0.9.3-models.scorer"

# # Load DeepSpeech model once
# print("[INFO] Loading DeepSpeech model...")
# model = deepspeech.Model(MODEL_PATH)
# model.enableExternalScorer(SCORER_PATH)
# print("[SUCCESS] Model loaded.")

# def convert_audio(input_path):
#     """ Convert any audio file to 16kHz, mono WAV format. """
#     output_path = "converted_audio.wav"
#     try:
#         print(f"[INFO] Converting {input_path} to DeepSpeech format...")
#         audio = AudioSegment.from_file(input_path)
#         audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
#         audio.export(output_path, format="wav")
#         return output_path
#     except Exception as e:
#         print(f"[ERROR] Audio conversion failed: {e}")
#         return None

# def read_wav_file(filename):
#     """ Reads a WAV file and converts it to NumPy array. """
#     try:
#         with wave.open(filename, "rb") as wf:
#             frames = wf.getnframes()
#             buffer = wf.readframes(frames)
#             audio = np.frombuffer(buffer, dtype=np.int16)
#         return audio
#     except Exception as e:
#         print(f"[ERROR] Failed to read WAV file: {e}")
#         return None

# @app.route('/speech-to-text', methods=['POST'])
# def speech_to_text():
#     """ API Endpoint to process uploaded audio and return transcribed text. """
#     if 'audio' not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400

#     file = request.files['audio']
#     file_path = "uploaded_audio.wav"
#     file.save(file_path)

#     # Convert audio if needed
#     if not file.filename.endswith(".wav"):
#         file_path = convert_audio(file_path)
#         if not file_path:
#             return jsonify({"error": "Audio conversion failed"}), 500

#     # Read and transcribe audio
#     audio_data = read_wav_file(file_path)
#     if audio_data is None:
#         return jsonify({"error": "Failed to read audio file"}), 500

#     text = model.stt(audio_data)
#     print(f"[INFO] Transcribed text: {text}")

#     return jsonify({"text": text})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


import os
import wave
import numpy as np
from flask import Flask, request, jsonify
from pydub import AudioSegment

# Initialize Flask App
app = Flask(__name__)

# Path to DeepSpeech binaries
MODEL_PATH = "./deepspeech-0.9.3-models.pbmm"
SCORER_PATH = "./deepspeech-0.9.3-models.scorer"

# Load DeepSpeech Model (with error handling)
try:
    import deepspeech
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCORER_PATH):
        raise FileNotFoundError("Model or scorer file not found.")
    model = deepspeech.Model(MODEL_PATH)
    model.enableExternalScorer(SCORER_PATH)
    print("[SUCCESS] DeepSpeech model loaded.")
except ImportError:
    print("[WARNING] DeepSpeech module not found. Falling back to dummy mode.")
    model = None
except Exception as e:
    print(f"[ERROR] Failed to load DeepSpeech model: {e}")
    model = None

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """API Endpoint to process audio and return transcribed text."""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['audio']
    file_path = "uploaded_audio.wav"
    file.save(file_path)

    # Convert audio to 16kHz mono WAV format
    try:
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(file_path, format="wav")
    except Exception as e:
        return jsonify({"error": f"Audio conversion failed: {e}"}), 500

    # Read WAV file
    try:
        with wave.open(file_path, "rb") as wf:
            frames = wf.getnframes()
            buffer = wf.readframes(frames)
            audio_data = np.frombuffer(buffer, dtype=np.int16)
    except Exception as e:
        return jsonify({"error": f"Failed to read WAV file: {e}"}), 500

    # Transcribe audio (if DeepSpeech is available)
    if model:
        text = model.stt(audio_data)
    else:
        text = "DeepSpeech is not available. Running in dummy mode."

    # Clean up: Delete the uploaded file
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"[WARNING] Failed to delete file: {e}")

    return jsonify({"text": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
