from fastapi import HTTPException, Header
from typing import Optional
from src.db.redis import redis_client

async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    key_data = redis_client.hgetall(f"apikey:{api_key}")
    
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return key_data