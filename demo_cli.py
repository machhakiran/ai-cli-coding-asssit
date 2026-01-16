import sys
import os
import time
from unittest.mock import MagicMock
from src.code_assistant import CodeAssistant
from src.config import AppConfig

# Mock for demo purposes since we can't run full RAG without ChromaDB here
def run_demo():
    print("Starting Demo Mode...")
    
    # Initialize with a dummy config
    config = AppConfig.from_env()
    
    # Mock the assistant to bypass initialization checks
    assistant = CodeAssistant(".", config=config)
    assistant.is_initialized = True
    
    # Mock the RAG chain
    assistant.rag_chain = MagicMock()
    assistant.rag_chain.ask.return_value = """
**Here is how the Code Assistant works:**

1. **Scans** your code using AST parsing
2. **Indexes** it using Vector Embeddings
3. **Retrieves** relevant context for your questions

To run this on your machine:
```bash
python main.py --repo . --interactive
```
"""
    assistant.rag_chain.ask_with_sources.return_value = (
        "This is a mocked answer demonstrating the UI.",
        [MagicMock(page_content="def example(): pass", metadata={"source": "demo.py"})]
    )

    # Launch the UI
    assistant.interactive_mode()

if __name__ == "__main__":
    run_demo()
