from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    API_KEY_PREFIX: str = "tts_"
    MAX_DEFAULT_USES: int = 100

    class Config:
        env_file = ".env"

settings = Settings()