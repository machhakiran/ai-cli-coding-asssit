import sys
import os
import logging
from src.code_parser import CodeParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_parser")

def test_parser():
    logger.info("Initializing CodeParser...")
    parser = CodeParser(chunk_size=1000, chunk_overlap=100)
    
    repo_path = os.getcwd() # Scan current dir
    logger.info(f"Scanning repository: {repo_path}")
    
    # scan for .py files
    try:
        documents = parser.parse_repository(repo_path, [".py"])
        logger.info(f"Successfully parsed {len(documents)} documents.")
        
        if documents:
            logger.info("First document sample:")
            print(documents[0].page_content[:200])
            print("...")
            
    except Exception as e:
        logger.error(f"Parsing failed: {e}")

if __name__ == "__main__":
    test_parser()
