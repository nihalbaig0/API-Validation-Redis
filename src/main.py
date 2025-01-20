from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import redis
import uuid
import time
from typing import Optional

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class APIKey(BaseModel):
    key: str
    client_name: str
    total_uses: int = 0
    max_uses: int = 100
    created_at: float

def generate_api_key() -> str:
    return f"tts_{uuid.uuid4().hex}"

def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    # Get key data from Redis
    key_data = redis_client.hgetall(f"apikey:{api_key}")
    
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Convert bytes to string/int
    key_info = {
        "client_name": key_data[b"client_name"].decode(),
        "total_uses": int(key_data[b"total_uses"]),
        "max_uses": int(key_data[b"max_uses"])
    }
    
    if key_info["total_uses"] >= key_info["max_uses"]:
        raise HTTPException(status_code=403, detail="API key usage limit exceeded")
    
    # Increment usage counter
    redis_client.hincrby(f"apikey:{api_key}", "total_uses", 1)
    
    return key_info

@app.post("/create-api-key")
async def create_api_key(client_name: str, max_uses: Optional[int] = 100):
    api_key = generate_api_key()
    
    # Store key data in Redis
    redis_client.hmset(f"apikey:{api_key}", {
        "client_name": client_name,
        "total_uses": 0,
        "max_uses": max_uses,
        "created_at": time.time()
    })
    
    return {
        "api_key": api_key,
        "client_name": client_name,
        "max_uses": max_uses,
        "message": "Please save this API key as it won't be shown again"
    }

@app.get("/key-info")
async def get_key_info(api_key: str = Header(..., alias="X-API-Key")):
    key_data = redis_client.hgetall(f"apikey:{api_key}")
    
    if not key_data:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {
        "client_name": key_data[b"client_name"].decode(),
        "total_uses": int(key_data[b"total_uses"]),
        "max_uses": int(key_data[b"max_uses"]),
        "remaining_uses": int(key_data[b"max_uses"]) - int(key_data[b"total_uses"])
    }

@app.post("/tts")
async def text_to_speech(text: str, key_info: dict = Depends(verify_api_key)):
    # Your TTS implementation here
    return {
        "message": f"Converting text to speech: {text}",
        "client": key_info["client_name"],
        "remaining_uses": key_info["max_uses"] - key_info["total_uses"]
    }

@app.get("/list-all-keys")
async def list_all_keys():
    # Get all keys matching the pattern "apikey:*"
    all_api_keys = redis_client.keys("apikey:*")
    
    if not all_api_keys:
        return {"message": "No API keys found", "keys": []}
    
    keys_info = []
    
    for key in all_api_keys:
        # Extract the actual API key from the Redis key
        api_key = key.decode().split(":")[1]
        key_data = redis_client.hgetall(key)
        
        # Convert bytes to appropriate types
        key_info = {
            "api_key": api_key,
            "client_name": key_data[b"client_name"].decode(),
            "total_uses": int(key_data[b"total_uses"]),
            "max_uses": int(key_data[b"max_uses"]),
            "remaining_uses": int(key_data[b"max_uses"]) - int(key_data[b"total_uses"]),
            "created_at": float(key_data[b"created_at"])
        }
        
        keys_info.append(key_info)
    
    return {
        "total_keys": len(keys_info),
        "keys": keys_info
    }