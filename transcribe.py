import os
import deepspeech
import numpy as np
import wave
from pydub import AudioSegment

# Paths to model and scorer files
MODEL_PATH = "deepspeech-0.9.3-models.pbmm"
SCORER_PATH = "deepspeech-0.9.3-models.scorer"
AUDIO_FILE = "harvard.wav"  # Change this to your actual input file

def convert_audio(input_path):
    """ Convert any audio file to 16kHz, mono WAV format compatible with DeepSpeech. """
    output_path = "converted_audio.wav"
    
    try:
        print(f"[INFO] Checking and converting {input_path} to DeepSpeech-compatible format...")
        
        # Load audio
        audio = AudioSegment.from_file(input_path)
        
        # Convert to 16kHz, mono, 16-bit PCM
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        
        # Export as WAV
        audio.export(output_path, format="wav")
        print(f"[SUCCESS] Audio converted: {output_path}")
        return output_path

    except Exception as e:
        print(f"[ERROR] Audio conversion failed: {e}")
        return None

def read_wav_file(filename):
    """ Reads a WAV file and converts it to NumPy array. """
    try:
        with wave.open(filename, "rb") as wf:
            rate = wf.getframerate()
            if rate != 16000:
                print("[WARNING] Audio sample rate is not 16kHz. Converting...")
                return None  # Trigger conversion
            
            frames = wf.getnframes()
            buffer = wf.readframes(frames)
            audio = np.frombuffer(buffer, dtype=np.int16)
        
        print("[INFO] WAV file successfully loaded.")
        return audio

    except Exception as e:
        print(f"[ERROR] Failed to read WAV file: {e}")
        return None

def transcribe_audio(audio_file):
    """ Transcribes the given audio file using DeepSpeech. """
    print("[INFO] Loading DeepSpeech model...")
    model = deepspeech.Model(MODEL_PATH)
    model.enableExternalScorer(SCORER_PATH)
    print("[SUCCESS] Model loaded successfully.")

    # Convert to compatible format if needed
    if not audio_file.endswith(".wav") or read_wav_file(audio_file) is None:
        print("[INFO] Converting audio file...")
        audio_file = convert_audio(audio_file)
        if not audio_file:
            print("[ERROR] Audio conversion failed. Exiting.")
            return

    # Read and transcribe audio
    print("[INFO] Reading and transcribing audio...")
    audio_data = read_wav_file(audio_file)
    if audio_data is None:
        print("[ERROR] Failed to process audio.")
        return

    print("[INFO] Transcribing...")
    text = model.stt(audio_data)
    print("\n🎤 **Recognized Text:**", text)

# Run transcription
if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCORER_PATH):
        print("[ERROR] Model files not found. Download from DeepSpeech GitHub.")
    elif not os.path.exists(AUDIO_FILE):
        print(f"[ERROR] Audio file '{AUDIO_FILE}' not found.")
    else:
        transcribe_audio(AUDIO_FILE)
