from datetime import datetime
from litellm import acompletion, image_generation
from app.config import settings
from app.models import ImageDescription, RouterAction
from app.prompts import (agent_system_prompt, router_system_prompt, image_generation_system_prompt)
from app.utils import format_conversation_for_llm
import httpx
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ai_response(conversation_history: list) -> str:
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    messages = [{"role": "system", "content": agent_system_prompt.format(current_date=current_date)}]
    
    for msg in conversation_history:
        messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
    
    response = await acompletion(
        api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, messages=messages, max_tokens=200
    )
    
    return response["choices"][0]["message"]["content"]

async def generate_image_dalle(conversation_history: list) -> str:
    
    prompt = await create_image_generation_prompt(conversation_history)
    response = image_generation(api_key=settings.OPENAI_API_KEY, prompt=prompt, model="dall-e-3")
    return response["data"][0]["url"]


async def generate_image(conversation_history: list) -> str:
    
    prompt = await create_image_generation_prompt(conversation_history)
    
    payload = {
    "response_image_type": "webp",
    "prompt": prompt,
    "seed": 123,
    "steps": 1,
    "width": 800,
    "height": 800,
    "image_num": 3
}
    headers = {
        "Content-Type": "application/json",
        "Authorization": settings.NOVITA_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(settings.NOVITA_API_URL, json=payload, headers=headers, timeout=30)
        response_json = response.json()
    
    return response_json["images"][0]["image_url"]


async def get_next_action(conversation_history: list) -> str:
    """
    Get the next action based on the conversation history.
    """
    history = format_conversation_for_llm(conversation_history)
    
    messages = [
        {"role": "system", "content": router_system_prompt},
        {"role": "user", "content": history}
    ]
    
    response = await acompletion(
        api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, messages=messages, max_tokens=200, response_format= RouterAction
    )
    
    return json.loads(response["choices"][0]["message"]["content"])


async def create_image_generation_prompt(conversation_history: list) -> str:
    """
    Generate image description prompt based on the conversation history.
    """
    history = format_conversation_for_llm(conversation_history)
    
    messages = [
        {"role": "system", "content": image_generation_system_prompt},
        {"role": "user", "content": history}
    ]
    
    response = await acompletion(
        api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, messages=messages, max_tokens=200, response_format=ImageDescription
    )
    
    image_description = json.loads(response["choices"][0]["message"]["content"])
    return image_description["prompt"]


    