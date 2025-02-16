from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.routes import router
from app.config import settings
import logging
import httpx


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup: Set up Telegram webhook
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/setWebhook",
            params={"url": "https://1a43-2601-cb-8000-33e0-cc36-3fe1-b97c-9890.ngrok-free.app/webhook"}
        )
        if response.status_code != 200 or not response.json().get("ok"):
            print(f"Error setting webhook: {response.status_code} - {response.text}")
            raise Exception("Failed to set Telegram webhook")
    
    # Yield control back to FastAPI
    yield

    # Shutdown: Clean up
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/deleteWebhook")

app = FastAPI(lifespan=lifespan)
app.include_router(router)


    



