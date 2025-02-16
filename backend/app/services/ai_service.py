from litellm import completion, image_generation
from app.config import settings
from app.prompts import agent_system_prompt
import httpx
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ai_response(conversation_history: list) -> str:
    messages = [{"role": "system", "content": agent_system_prompt}]
    
    for msg in conversation_history:
        messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
    
    response = completion(
        api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, messages=messages, max_tokens=200
    )
    
    return response["choices"][0]["message"]["content"]

async def generate_image_dalle(prompt: str) -> str:
    response = image_generation(api_key=settings.OPENAI_API_KEY, prompt=prompt, model="dall-e-3")
    return response["data"][0]["url"]


async def generate_image(prompt: str) -> str:
    
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
    
    logger.info(f'---------->{response_json}')
    return response_json["images"][0]["image_url"]