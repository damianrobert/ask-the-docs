from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    # LLM
    llm_backend: Literal["ollama", "anthropic"] = "ollama"
    llm_model: str = "llama3.2:3b"
    ollama_url: str = "http://localhost:11434"
    anthropic_api_key: SecretStr | None = None

    # Retrieval
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    top_k: int = 5
