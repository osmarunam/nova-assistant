import httpx
from app.config import settings
from app.kokoro_tts.tts import kTTS
import tempfile
import soundfile as sf
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def send_telegram_message(chat_id: int, text: str):
    """Send message to Telegram chat"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.TELEGRAM_API_BASE}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            }
        )
        return response.json()
    
    
async def send_telegram_audio(chat_id: int, text: str):
    """Send audio message to Telegram chat"""
    try:
        # Convert text to speech (using your kTTS function)
        audio_data = await text_to_speech(text)
        
        async with httpx.AsyncClient() as client:
            # Prepare the multipart form data
            files = {
                'audio': ('message.wav', audio_data, 'audio/wav')  # Changed to WAV format
            }
            
            data = {
                'chat_id': chat_id,
                'title': 'Voice Message',
                'performer': 'Nova Assistant',
                'caption': text[:100] + '...' if len(text) > 100 else text
            }
            
            # Send using sendAudio endpoint
            response = await client.post(
                f"{settings.TELEGRAM_API_BASE}/sendAudio",
                data=data,
                files=files
            )
            
            if not response.json().get('ok'):
                # Fallback to sendVoice if sendAudio fails
                files = {'voice': ('voice.wav', audio_data, 'audio/wav')}  # Changed to WAV
                response = await client.post(
                    f"{settings.TELEGRAM_API_BASE}/sendVoice",
                    data={'chat_id': chat_id},
                    files=files
                )
            
            return response.json()
            
    except Exception as e:
        print(f"Error sending audio: {str(e)}")  # Added for debugging
        # If audio sending fails, fallback to text
        return await send_telegram_message(chat_id, f"Could not send audio. Here's the text: {text}")
    

async def send_telegram_image(chat_id: int, image_url: str):
    """Send image to Telegram chat"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.TELEGRAM_API_BASE}/sendPhoto",
            json={
                "chat_id": chat_id,
                "photo": image_url
            }
        )
        return response.json()
   
async def text_to_speech(text: str) -> bytes:
    """Convert text to speech"""
    samples, sample_rate = kTTS(text=text, language="en-us")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        sf.write(temp_audio_path, samples, sample_rate)  # Save audio as WAV
        logger.info(f"Saved audio to {temp_audio_path}")

    try:
        with open(temp_audio_path, 'rb') as audio_file:
            return audio_file.read()
    finally:
        os.unlink(temp_audio_path)  # Ensure the temp file is deleted after use

