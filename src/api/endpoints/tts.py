from fastapi import APIRouter, Depends
from src.core.security import verify_api_key
from src.models.api_key import APIKey

router = APIRouter()

@router.post("/tts")
async def text_to_speech(text: str, key_info: dict = Depends(verify_api_key)):
    # TTS implementation here
    return {
        "message": f"Converting text to speech: {text}",
        "client": key_info["client_name"],
        "remaining_uses": int(key_info["max_uses"]) - int(key_info["total_uses"])
    }