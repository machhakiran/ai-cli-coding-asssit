from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from config import LLMConfig
import logging

logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def create_llm(config: LLMConfig) -> BaseChatModel:
        if config.provider == "openai":
            if not config.api_key:
                raise ValueError("OpenAI API key is required for OpenAI provider")
            logger.info(f"Initializing OpenAI LLM with model {config.model_name}")
            return ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                api_key=config.api_key
            )
        elif config.provider == "ollama":
            logger.info(f"Initializing Ollama LLM with model {config.model_name} at {config.base_url}")
            return ChatOllama(
                model=config.model_name,
                temperature=config.temperature,
                base_url=config.base_url
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    @staticmethod
    def create_embeddings(config: LLMConfig) -> Embeddings:
        if config.provider == "openai":
            if not config.api_key:
                raise ValueError("OpenAI API key is required for OpenAI provider")
            logger.info(f"Initializing OpenAI Embeddings with model {config.embedding_model}")
            return OpenAIEmbeddings(
                model=config.embedding_model,
                api_key=config.api_key
            )
        elif config.provider == "ollama":
            logger.info(f"Initializing Ollama Embeddings with model {config.embedding_model}")
            return OllamaEmbeddings(
                model=config.embedding_model,
                base_url=config.base_url
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")
