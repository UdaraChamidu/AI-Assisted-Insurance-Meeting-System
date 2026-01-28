"""
Configuration management using Pydantic Settings.
All configuration values are loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # Application Settings
    app_env: str = "development"
    app_debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/insurance_agent"
    
    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Session Management
    session_expiry_hours: int = 24
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    # Microsoft Graph API
    ms_client_id: str
    ms_client_secret: str
    ms_tenant_id: str
    ms_booking_business_id: str
    
    # Zoom Configuration
    zoom_account_id: str = ""
    zoom_client_id: str = ""
    zoom_client_secret: str = ""
    zoom_api_key: str = ""
    zoom_api_secret: str = ""
    zoom_sdk_key: str = ""
    zoom_sdk_secret: str = ""
    
    # Email (SMTP)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    
    # Deepgram
    deepgram_api_key: str
    
    # Google Gemini
    google_api_key: str
    
    # AI Provider
    ai_provider: str = "openai" # gemini or openai
    
    # Gemini
    gemini_model: str = "gemini-1.5-pro"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # Pinecone
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "insurance-knowledge"
    
    # ElevenLabs (Optional)
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None
    
    # Domain
    domain: str = "https://ai-assisted-insurance-meeting-syste.vercel.app"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"
    
    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins."""
        if self.is_production:
            return [self.domain, self.frontend_url]
        return [self.frontend_url, "http://localhost:5173", "http://localhost:3000"]


# Global settings instance
settings = Settings() # Force reload 11
