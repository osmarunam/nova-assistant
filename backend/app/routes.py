from fastapi import APIRouter, HTTPException
from app.models import TelegramUpdate
from app.services.telegram_service import send_telegram_message, send_telegram_image, text_to_speech
from app.services.ai_service import generate_image, get_ai_response, generate_image_dalle, get_next_action
from app.conversation import conversation_state
from app.services.telegram_service import send_telegram_audio
from app.config import settings
from app.services.stt import transcribe
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Server is running"}


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram messages"""
    # logger.info(f"+++++++++++++++++++++++++++++++++Received message from user: {update.message}")
    if not update.message:
        return {"status": "ok"}
    
    chat_id = update.message["chat"]["id"]
    user_message = None
    message_type = "text"
    
    # Handle different message types
    if "text" in update.message:
        user_message = update.message["text"]
    elif "voice" in update.message:
        # Handle voice message
        voice_file_id = update.message["voice"]["file_id"]
        voice_data = await download_voice_message(voice_file_id)
        user_message = await transcribe(voice_data)
        message_type = "voice"
        if not user_message:
            await send_telegram_message(
                chat_id,
                "I apologize, but I'm having trouble processing your audio message. Can you type it?"
            )
            return {"status": "ok"}
    
    # Add user message to conversation history
    conversation_state.add_message(chat_id, "user", user_message, message_type)
    
    # Get conversation history
    history = conversation_state.get_conversation_history(chat_id)
    
    try:
        ai_response = await get_ai_response(history)
        
        # Send response back to user
        await send_telegram_message(chat_id, ai_response)
        
        # Add AI response to conversation history
        conversation_state.add_message(chat_id, "assistant", ai_response)
        
        next_action = await get_next_action(history)
        logger.info(f"Next action: {next_action['response_type']}")
        
        if next_action["response_type"] == "image":
            # image_url = await generate_image_dalle(history)
            image_url = await generate_image(history)
            logger.info(f"+++++++image_url: {image_url}")
            await send_telegram_image(chat_id, image_url)
            
        elif next_action["response_type"] == "audio":
                audio_data = await text_to_speech(ai_response)
                await send_telegram_audio(chat_id, ai_response)
            
    except Exception as e:
        await send_telegram_message(
            chat_id,
            "I apologize, but I'm having trouble processing your message right now. Please try again later."
        )
        logger.error(f"======>Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "ok"}


async def download_voice_message(file_id: str) -> bytes:
    """Download voice message from Telegram"""
    async with httpx.AsyncClient() as client:
        # Get file path
        response = await client.get(
            f"{settings.TELEGRAM_API_BASE}/getFile",
            params={"file_id": file_id}
        )
        file_path = response.json()["result"]["file_path"]
        
        # Download file
        file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_TOKEN}/{file_path}"
        response = await client.get(file_url)
        return response.content