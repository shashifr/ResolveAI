import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Settings:
    # API Credentials
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
    
    # Database Config
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///ai_customer_support.db")
    
    # Server Config
    PORT: int = int(os.environ.get("PORT", "8000"))
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    
    # API Security Credentials (for demo gateway verification)
    API_BEARER_TOKEN: str = "resolveai-demo-token"

settings = Settings()
