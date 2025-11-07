"""Configuration management for RFP Draft Booster."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application
    app_name: str = "RFP Draft Booster"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "DEBUG"  # Default to DEBUG per BairesDev standards
    
    # File Upload
    max_file_size: int = 52428800  # 50MB in bytes
    allowed_extensions: list = [".pdf"]
    upload_directory: str = "data/uploads/"
    temp_directory: str = "data/temp/"
    
    # LLM Configuration
    llm_provider: str = "gemini"  # gemini | groq | ollama
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    # Processing
    min_confidence: float = 0.7
    match_threshold: float = 0.7
    auto_approve_threshold: float = 0.85
    
    # Risk Detection
    critical_risks_block_draft: bool = True
    risk_confidence_threshold: float = 0.6
    
    # Draft Generation
    min_draft_word_count: int = 500
    max_draft_word_count: int = 10000
    
    # Google Docs
    gdocs_credentials_path: Optional[str] = None
    
    # Database (future)
    database_url: Optional[str] = "sqlite:///data/rfp_booster.db"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

