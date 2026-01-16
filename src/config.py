import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    provider: str = "ollama"  # ollama, openai
    model_name: str = "llama3"
    temperature: float = 0.0
    base_url: Optional[str] = "http://localhost:11434"
    api_key: Optional[str] = None
    embedding_model: str = "llama3" # or text-embedding-3-large

@dataclass
class AppConfig:
    llm: LLMConfig
    persist_directory: str = "./chroma_db"
    chunk_size: int = 2000
    chunk_overlap: int = 200

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "ollama"),
                model_name=os.getenv("LLM_MODEL", "llama3.2"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
                api_key=os.getenv("OPENAI_API_KEY"),
                embedding_model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text" if os.getenv("LLM_PROVIDER", "ollama") == "ollama" else "text-embedding-3-large")
            ),
            persist_directory=os.getenv("DB_PATH", "./chroma_db")
        )
