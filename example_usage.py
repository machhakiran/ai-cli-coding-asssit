#!/usr/bin/env python3
"""
Example usage demonstrating the AI Code Assistant capabilities.
This shows how to programmatically use the assistant in your own scripts.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from code_assistant import CodeAssistant


def example_basic_usage():
    """Basic usage example: Index a repository and ask questions."""
    
    print("="*80)
    print("EXAMPLE 1: Basic Usage")
    print("="*80)
    
    assistant = CodeAssistant(
        repo_path="./src",
        persist_directory="./example_chroma_db"
    )
    
    print("\n1. Indexing repository...")
    assistant.index_repository(file_extensions=['.py'])
    
    print("\n2. Asking a question...")
    question = "What are the main classes in this codebase?"
    answer = assistant.ask(question)
    
    print(f"\nQ: {question}")
    print(f"A: {answer}\n")


def example_with_sources():
    """Example showing source documents with answers."""
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Showing Source Documents")
    print("="*80)
    
    assistant = CodeAssistant(
        repo_path="./src",
        persist_directory="./example_chroma_db"
    )
    
    if not assistant.vector_store.load_existing():
        assistant.index_repository(file_extensions=['.py'])
    else:
        print("Loaded existing index")
        retriever = assistant.vector_store.get_retriever()
        from rag_chain import RAGChain
        repo_map = assistant.repo_mapper.get_compact_map(
            extensions={'.py'},
            max_lines=150
        )
        assistant.rag_chain = RAGChain(retriever, repo_map=repo_map)
        assistant.is_initialized = True
    
    question = "How does the vector store work?"
    print(f"\nQ: {question}\n")
    
    answer = assistant.ask(question, show_sources=True)


def example_repository_structure():
    """Example showing repository structure mapping."""
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Repository Structure")
    print("="*80)
    
    assistant = CodeAssistant(
        repo_path="./src",
        persist_directory="./example_chroma_db"
    )
    
    structure = assistant.get_repository_structure()
    print(structure)


def example_multiple_languages():
    """Example indexing multiple programming languages."""
    
    print("\n" + "="*80)
    print("EXAMPLE 4: Multiple Languages")
    print("="*80)
    
    assistant = CodeAssistant(
        repo_path="./example_project",
        persist_directory="./multilang_chroma_db"
    )
    
    print("\nIndexing Python, JavaScript, and TypeScript files...")
    assistant.index_repository(
        file_extensions=['.py', '.js', '.ts'],
        force_reindex=True
    )
    
    question = "Show me all the main functions across all languages"
    answer = assistant.ask(question)
    
    print(f"\nQ: {question}")
    print(f"A: {answer}\n")


if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    example_basic_usage()
    example_with_sources()
    example_repository_structure()
