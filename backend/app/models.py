from pydantic import BaseModel
from typing import Dict, Optional

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict] = None
