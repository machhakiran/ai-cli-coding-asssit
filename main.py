#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from code_assistant import CodeAssistant
from config import AppConfig, LLMConfig

def main():
    parser = argparse.ArgumentParser(
        description='AI Code Assistant - Production Grade Implementation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --repo ./my_project --interactive
  python main.py --repo ./my_project --query "How does the authentication work?"
  python main.py --repo ./my_project --provider openai --model gpt-4
        """
    )
    
    parser.add_argument(
        '--repo',
        type=str,
        required=True,
        help='Path to the code repository to analyze'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Start interactive Q&A mode'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Ask a single question about the codebase'
    )
    
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.py'],
        help='File extensions to index (default: .py)'
    )
    
    parser.add_argument(
        '--reindex',
        action='store_true',
        help='Force rebuild the vector index'
    )
    
    parser.add_argument(
        '--show-sources',
        action='store_true',
        help='Show source documents with answers'
    )
    
    parser.add_argument(
        '--show-structure',
        action='store_true',
        help='Display repository structure and exit'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='./chroma_db',
        help='Path to store vector database (default: ./chroma_db)'
    )

    parser.add_argument(
        '--provider',
        type=str,
        default='ollama',
        choices=['ollama', 'openai'],
        help='LLM provider to use (default: ollama)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='llama3',
        help='Model name to use (default: llama3)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.repo):
        logger.error(f"Repository path does not exist: {args.repo}")
        sys.exit(1)
    
    # Initialize configuration
    config = AppConfig.from_env()
    config.persist_directory = args.db_path
    config.llm.provider = args.provider
    config.llm.model_name = args.model

    if args.provider == 'openai' and not config.llm.api_key:
        logger.error("OPENAI_API_KEY environment variable not set for OpenAI provider")
        sys.exit(1)
    
    logger.info("Initializing AI Code Assistant...")
    logger.info(f"Repository: {args.repo}")
    logger.info(f"Provider: {args.provider}, Model: {args.model}")
    
    try:
        assistant = CodeAssistant(
            repo_path=args.repo,
            config=config
        )
        
        assistant.index_repository(
            file_extensions=args.extensions,
            force_reindex=args.reindex
        )
        
        if args.show_structure:
            print("\n" + "="*80)
            print(assistant.get_repository_structure())
            print("="*80)
            return
        
        if args.interactive:
            assistant.interactive_mode()
        elif args.query:
            print("\n" + "="*80)
            print(f"Question: {args.query}")
            print("="*80)
            answer = assistant.ask(args.query, show_sources=args.show_sources)
            if not args.show_sources:
                print(f"\nAnswer: {answer}")
            print("="*80)
        else:
            logger.warning("No action specified. Use --interactive or --query")
            print("Run with --help for usage information")
            
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
