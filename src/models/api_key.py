from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class APIKey(BaseModel):
    key: str
    client_name: str
    total_uses: int = 0
    max_uses: int = 100
    created_at: datetime

class APIKeyCreate(BaseModel):
    client_name: str
    max_uses: Optional[int] = None