import sys
import os
import logging
from src.config import AppConfig
from src.llm_factory import LLMFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_generation")

def test_generation():
    logger.info("Testing LLM Generation (Bypassing RAG)...")
    
    try:
        # 1. Load Config
        config = AppConfig.from_env()
        
        # 2. Initialize LLM directly
        llm = LLMFactory.create_llm(config.llm)
        
        # 3. Create a prompt
        prompt = "Generate a simple, single-file HTML/JS application with a button that changes color when clicked. partial code only."
        logger.info(f"Sending prompt to {config.llm.provider}/{config.llm.model_name}: '{prompt}'")
        
        # 4. Invoke
        response = llm.invoke(prompt)
        
        print("\n" + "="*80)
        print("GENERATED CONTENT:")
        print("="*80)
        print(response.content)
        print("="*80 + "\n")
        
        logger.info("Generation test completed successfully.")
        
    except Exception as e:
        logger.error(f"Generation test failed: {e}")

if __name__ == "__main__":
    test_generation()
