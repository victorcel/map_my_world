import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App config
    PROJECT_NAME: str = "MapMyWorld API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Location management API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mapmyworld.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
    
    # Geo search defaults
    MAX_SEARCH_RADIUS_KM: float = float(os.getenv("MAX_SEARCH_RADIUS_KM", "50.0"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "100"))

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()