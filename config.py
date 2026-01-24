from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    CORS_ORIGINS: str
    APP_BASE_URL: str 

    class Config:
        env_file = ".env"

settings = Settings()