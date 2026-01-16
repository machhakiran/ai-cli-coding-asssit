import sys
import os
import logging
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from config import AppConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_config")

try:
    logger.info("Testing AppConfig...")
    config = AppConfig.from_env()
    
    logger.info(f"Loaded Configuration:")
    logger.info(f"Persist Directory: {config.persist_directory}")
    logger.info(f"LLM Provider: {config.llm.provider}")
    logger.info(f"LLM Model: {config.llm.model_name}")
    logger.info(f"Base URL: {config.llm.base_url}")
    logger.info(f"Embedding Model: {config.llm.embedding_model}")
    
    print("\nConfiguration Object:")
    print(config)
    
except Exception as e:
    logger.error(f"Config test failed: {e}")
