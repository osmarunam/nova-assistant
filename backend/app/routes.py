from fastapi import APIRouter, HTTPException
from app.models import TelegramUpdate
from app.services.telegram_service import send_telegram_message, send_telegram_image
from app.services.ai_service import generate_image, get_ai_response, generate_image_dalle
from app.conversation import conversation_state
from app.services.telegram_service import send_telegram_audio
from app.config import settings
import logging
import httpx


router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def root():
    return {"message": "Server is running"}


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Handle incoming Telegram messages"""
    logger.info(f"===============>Received update: {update}")
    if not update.message or not update.message.get("text"):
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
        # user_message = await speech_to_text(voice_data)
        message_type = "voice"
    
    
    logger.info(f"Received message from user {chat_id}: {user_message}")
    
    # Add user message to conversation history
    conversation_state.add_message(chat_id, "user", user_message, message_type)
    
    # Get conversation history
    history = conversation_state.get_conversation_history(chat_id)
    # logger.info(f"Conversation history: {history}")
    
    # Get AI response
    try:
        if 'image' in user_message:
        
            # image_url = await generate_image_dalle(user_message)
            image_url = await generate_image(user_message)
            await send_telegram_image(chat_id, image_url)
            
        else:
            ai_response = await get_ai_response(history)
            
            # Add AI response to conversation history
            conversation_state.add_message(chat_id, "assistant", ai_response)
            
            # Send response back to user
            await send_telegram_message(chat_id, ai_response)
            if 'audio' in user_message:
                # audio_data = await text_to_speech(ai_response)
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