import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    upstage_api_key: str = ""  # Optional, can be set via environment or runtime
    secret_key: str = "your-secret-key-change-this-in-production"
    
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # Environment
    environment: str = "development"
    
    # File upload settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "uploads"
    allowed_extensions: list = [".pdf"]
    
    # RAG settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "solar-embedding-1-large"  # Upstage embedding model
    llm_model: str = "solar-1-mini-chat"  # Upstage LLM model
    max_tokens: int = 4000
    
    # FAISS settings
    faiss_index_path: str = "faiss_index"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
