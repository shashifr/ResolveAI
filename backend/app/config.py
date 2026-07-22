from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # API Credentials
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # Database Config
    DATABASE_URL: str = "sqlite:///ai_customer_support.db"
    
    # Server Config
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # API Security Credentials (for demo gateway verification)
    API_BEARER_TOKEN: str = "resolveai-demo-token"
    
    # Security Options
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "https://resolveai-navy.vercel.app"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def api_key(self) -> str:
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY

settings = Settings()
# Ensure backward compatibility if they used settings.GEMINI_API_KEY and it was empty but GOOGLE_API_KEY was set
if not settings.GEMINI_API_KEY and settings.GOOGLE_API_KEY:
    settings.GEMINI_API_KEY = settings.GOOGLE_API_KEY
