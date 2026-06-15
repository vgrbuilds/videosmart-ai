import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "VideoSmart AI API"
    API_V1_STR: str = "/api"
    CLIENT_URL: str = "http://localhost:5173"
    
    # MongoDB Config
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "videosmart"
    
    # Gemini API Config
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_MODEL_NAME: Optional[str] = None
    
    # Cloudinary Config
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # JWT Auth Config
    JWT_SECRET: str = "supersecretjwtsecretkeychangeinproduction"
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # Audio settings
    DOWNLOAD_DIR: str = "downloads"
    
    @property
    def gemini_model_to_use(self) -> str:
        return self.GEMINI_MODEL_NAME or self.GEMINI_MODEL
        
    def __init__(self, **values):
        super().__init__(**values)
        if self.JWT_SECRET_KEY:
            self.JWT_SECRET = self.JWT_SECRET_KEY
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
