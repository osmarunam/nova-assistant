from kokoro_onnx import Kokoro
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the script
TTS_FILES_DIR = os.path.join(BASE_DIR, "..", "tts_files")  # Move up one level

kokoro = Kokoro(
    os.path.abspath(os.path.join(TTS_FILES_DIR, "kokoro-v1.0.onnx")),
    os.path.abspath(os.path.join(TTS_FILES_DIR, "voices-v1.0.bin"))
)

def kTTS(text: str, language="en-us") -> bytes:
    """Convert text to speech using kokoro"""
    samples, sample_rate = kokoro.create(
        text, voice="af_sarah", speed=1.0, lang=language
    )
    return samples, sample_rate