from code_parser import CodeParser
from vector_store import VectorStore
from repo_mapper import RepoMapper
from rag_chain import RAGChain
import os
from typing import Optional


class CodeAssistant:
    """
    Main class that orchestrates all components of the AI code assistant.
    This is how tools like Cursor, Windsurf, and Antigravity work internally.
    """
    
    def __init__(self, repo_path: str, persist_directory: str = "./chroma_db"):
        self.repo_path = repo_path
        self.persist_directory = persist_directory
        
        self.parser = CodeParser(chunk_size=2000, chunk_overlap=200)
        self.vector_store = VectorStore(persist_directory=persist_directory)
        self.repo_mapper = RepoMapper(repo_path)
        self.rag_chain: Optional[RAGChain] = None
        
        self.is_initialized = False
        
    def index_repository(self, file_extensions: list = None, force_reindex: bool = False) -> None:
        """
        Index the repository by parsing code and storing in vector database.
        
        Args:
            file_extensions: List of file extensions to index (e.g., ['.py', '.js'])
            force_reindex: If True, rebuild index even if it exists
        """
        if file_extensions is None:
            file_extensions = ['.py']
            
        if not force_reindex and self.vector_store.load_existing():
            print("Loaded existing index from disk")
        else:
            print(f"Indexing repository at: {self.repo_path}")
            print(f"Processing file types: {', '.join(file_extensions)}")
            
            documents = self.parser.parse_repository(self.repo_path, file_extensions)
            
            if not documents:
                raise ValueError("No documents were parsed. Check repository path and file extensions.")
            
            self.vector_store.initialize_from_documents(documents)
            print(f"Successfully indexed {len(documents)} code chunks")
        
        print("\nBuilding repository map...")
        repo_map = self.repo_mapper.get_compact_map(
            extensions=set(file_extensions),
            max_lines=150
        )
        
        print("Initializing RAG chain...")
        retriever = self.vector_store.get_retriever()
        self.rag_chain = RAGChain(retriever, repo_map=repo_map)
        
        self.is_initialized = True
        print("\nCode Assistant ready!")
        
    def ask(self, question: str, show_sources: bool = False) -> str:
        """
        Ask a question about the codebase.
        
        Args:
            question: Question about the code
            show_sources: If True, also display source documents
            
        Returns:
            Answer from the AI assistant
        """
        if not self.is_initialized:
            raise ValueError("Assistant not initialized. Call index_repository() first.")
        
        if show_sources:
            answer, sources = self.rag_chain.ask_with_sources(question)
            
            print("\n" + "="*80)
            print("ANSWER:")
            print("="*80)
            print(answer)
            
            print("\n" + "="*80)
            print("SOURCE DOCUMENTS:")
            print("="*80)
            for i, doc in enumerate(sources, 1):
                source = doc.metadata.get('source', 'Unknown')
                print(f"\n[{i}] {source}")
                print("-" * 40)
                print(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
            
            return answer
        else:
            return self.rag_chain.ask(question)
    
    def interactive_mode(self) -> None:
        """
        Start an interactive Q&A session with the code assistant.
        """
        if not self.is_initialized:
            raise ValueError("Assistant not initialized. Call index_repository() first.")
        
        print("\n" + "="*80)
        print("INTERACTIVE CODE ASSISTANT")
        print("="*80)
        print("Ask questions about your codebase. Type 'exit' or 'quit' to stop.")
        print("Type 'sources' to see source documents with answers.")
        print("="*80 + "\n")
        
        show_sources = False
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break
                    
                if user_input.lower() == 'sources':
                    show_sources = not show_sources
                    status = "enabled" if show_sources else "disabled"
                    print(f"\nSource documents display {status}")
                    continue
                
                if not user_input:
                    continue
                
                print("\nAssistant: ", end="", flush=True)
                answer = self.ask(user_input, show_sources=show_sources)
                
                if not show_sources:
                    print(answer)
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.")
    
    def get_repository_structure(self) -> str:
        """
        Get the repository structure map.
        
        Returns:
            Formatted repository structure
        """
        return self.repo_mapper.generate_context_map()
