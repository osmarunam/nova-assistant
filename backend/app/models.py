from pydantic import BaseModel, Field
from typing import Dict, Optional

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict] = None
    
    
class RouterAction(BaseModel):
    response_type: str = Field(description="The response type to give to the user. It must be one of: 'text', 'image' or 'audio'")

class ImageDescription(BaseModel):
    prompt: str = Field(description="The prompt to use for image generation")