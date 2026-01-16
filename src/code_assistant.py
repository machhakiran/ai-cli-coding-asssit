from code_parser import CodeParser
from vector_store import VectorStore
from repo_mapper import RepoMapper
from rag_chain import RAGChain
from config import AppConfig
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CodeAssistant:
    """
    Main class that orchestrates all components of the AI code assistant.
    This is how tools like Cursor, Windsurf, and Antigravity work internally.
    """
    
    def __init__(self, repo_path: str, config: AppConfig = None):
        self.repo_path = repo_path
        self.config = config or AppConfig.from_env()
        self.persist_directory = self.config.persist_directory
        
        self.parser = CodeParser(
            chunk_size=self.config.chunk_size, 
            chunk_overlap=self.config.chunk_overlap
        )
        self.vector_store = VectorStore(persist_directory=self.persist_directory, config=self.config.llm)
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
            logger.info("Loaded existing index from disk")
        else:
            logger.info(f"Indexing repository at: {self.repo_path}")
            logger.info(f"Processing file types: {', '.join(file_extensions)}")
            
            documents = self.parser.parse_repository(self.repo_path, file_extensions)
            
            if not documents:
                raise ValueError("No documents were parsed. Check repository path and file extensions.")
            
            self.vector_store.initialize_from_documents(documents)
            logger.info(f"Successfully indexed {len(documents)} code chunks")
        
        logger.info("Building repository map...")
        repo_map = self.repo_mapper.get_compact_map(
            extensions=set(file_extensions),
            max_lines=150
        )
        
        logger.info("Initializing RAG chain...")
        retriever = self.vector_store.get_retriever()
        self.rag_chain = RAGChain(
            retriever, 
            repo_map=repo_map,
            config=self.config.llm
        )
        
        self.is_initialized = True
        logger.info("Code Assistant ready!")
        
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
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            from rich.panel import Panel
            from rich.prompt import Prompt
            from rich.style import Style
            from rich.live import Live
            from rich.spinner import Spinner
            
            console = Console()
        except ImportError:
            # Fallback for when rich is not installed
            print("Rich library not found. Falling back to simple mode.")
            return self._simple_interactive_mode()

        if not self.is_initialized:
            raise ValueError("Assistant not initialized. Call index_repository() first.")
        
        # ASCII Art Banner
        banner = r"""
    __ ___         _           _ 
   / //_ /__ __ __(_)  ___ _  (_)
  / ,< / _ `/ |/ / /  / _ `/ / / 
 /_/|_|\_,_/|___/_/   \_,_/ /_/  
                                 
      Code Assistant AI
        """
        
        console.print(Panel(
            banner, 
            style="bold blue", 
            subtitle="[dim]Powered by RAG & LLMs[/dim]",
            width=60
        ))
        
        console.print("[green]✓ System Ready[/green]")
        console.print("[dim]Type 'exit' to quit, 'sources' to toggle source visibility[/dim]\n")
        
        show_sources = False
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[yellow]Goodbye![/yellow]")
                    break
                    
                if user_input.lower() == 'sources':
                    show_sources = not show_sources
                    status = "[green]ON[/green]" if show_sources else "[red]OFF[/red]"
                    console.print(f"Source documents: {status}")
                    continue
                
                if not user_input:
                    continue
                
                # Show spinner while thinking
                with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots"):
                    if show_sources:
                         answer, sources = self.rag_chain.ask_with_sources(user_input)
                    else:
                         answer = self.rag_chain.ask(user_input)
                         sources = []

                # Print Answer
                console.print("\n[bold purple]Assistant:[/bold purple]")
                console.print(Markdown(answer))
                
                # Print Sources if enabled
                if show_sources and sources:
                     console.print("\n[bold yellow]Sources:[/bold yellow]")
                     for i, doc in enumerate(sources, 1):
                        source = doc.metadata.get('source', 'Unknown')
                        content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                        console.print(Panel(
                            content,
                            title=f"[{i}] {source}",
                            border_style="yellow dim"
                        ))

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                console.print(f"\n[red]Error: {e}[/red]")
                
    def _simple_interactive_mode(self) -> None:
        """Fallback mode without rich"""
        print("\n" + "="*80)
        print("INTERACTIVE CODE ASSISTANT")
        print("="*80)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                print("\nAssistant: ", end="", flush=True)
                print(self.rag_chain.ask(user_input))
            except Exception:
                break
    
    def get_repository_structure(self) -> str:
        """
        Get the repository structure map.
        
        Returns:
            Formatted repository structure
        """
        return self.repo_mapper.generate_context_map()
