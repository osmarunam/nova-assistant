from app.config import settings
from groq import Groq
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def transcribe(audio_bytes: bytes, model: str = "distil-whisper-large-v3-en", language: str = "en", temperature: float = 0.0) -> str:
    """
    Transcribe audio bytes using the Groq API.

    :param audio_bytes: Audio file content in bytes.
    :param model: Model to use for transcription.
    :param language: Language of the audio.
    :param temperature: Sampling temperature.
    :return: Transcription text.
    """
    # Initialize the Groq client
    client = Groq(api_key=settings.GROQ_API_KEY)

    # Create a transcription of the audio file
    transcription = client.audio.transcriptions.create(
        file=("audio.m4a", audio_bytes),  # Fake filename for the request
        model=model,  
        language=language,  
        temperature=temperature,  
        response_format="json"  
    )

    logger.info(f"Transcription: {transcription}")
    
    return transcription.text
