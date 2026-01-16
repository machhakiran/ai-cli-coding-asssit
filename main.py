#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from code_assistant import CodeAssistant


def main():
    parser = argparse.ArgumentParser(
        description='AI Code Assistant - Understanding how Cursor, Windsurf, and Antigravity work',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --repo ./my_project --interactive
  python main.py --repo ./my_project --query "How does the authentication work?"
  python main.py --repo ./my_project --extensions .py .js --reindex
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
    
    args = parser.parse_args()
    
    if not os.path.exists(args.repo):
        print(f"Error: Repository path does not exist: {args.repo}")
        sys.exit(1)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("Initializing AI Code Assistant...")
    print(f"Repository: {args.repo}")
    print(f"Extensions: {', '.join(args.extensions)}")
    
    assistant = CodeAssistant(
        repo_path=args.repo,
        persist_directory=args.db_path
    )
    
    try:
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
            print("\nNo action specified. Use --interactive or --query")
            print("Run with --help for usage information")
            
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
