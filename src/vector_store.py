try:
    from langchain_chroma import Chroma
except ImportError:
    Chroma = None
    
from langchain_core.documents import Document
from typing import List
import os
import logging
from config import LLMConfig
from llm_factory import LLMFactory

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Manages vector storage using ChromaDB for semantic code search.
    Uses embeddings to enable searching by meaning rather than keywords.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db", config: LLMConfig = None):
        self.persist_directory = persist_directory
        self.config = config or LLMConfig()
        self.db = None
        self.retriever = None
        if Chroma is None:
            logger.warning("ChromaDB not installed. Vector storage will not work.")
        
    def initialize_from_documents(self, documents: List[Document]) -> None:
        """
        Initialize vector store from code documents.
        
        Args:
            documents: List of Document objects containing code chunks
        """
        if not documents:
            raise ValueError("Cannot initialize vector store with empty documents")
            
        embeddings = LLMFactory.create_embeddings(self.config)
        
        self.db = Chroma.from_documents(
            documents,
            embeddings,
            persist_directory=self.persist_directory
        )
        
        self.retriever = self.db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 8}
        )
        
        logger.info(f"Vector store initialized with {len(documents)} documents")
        logger.info(f"Using MMR (Maximal Marginal Relevance) for diverse retrieval")
    
    def load_existing(self) -> bool:
        """
        Load existing vector store from disk if available.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.persist_directory):
            return False
            
        try:
            embeddings = LLMFactory.create_embeddings(self.config)
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings
            )
            
            self.retriever = self.db.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 8}
            )
            
            logger.info(f"Loaded existing vector store from {self.persist_directory}")
            return True
        except Exception as e:
            logger.error(f"Error loading existing vector store: {e}")
            return False
    
    def search(self, query: str, k: int = 8) -> List[Document]:
        """
        Search for relevant code chunks using semantic similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant Document objects
        """
        if not self.retriever:
            raise ValueError("Vector store not initialized. Call initialize_from_documents() first.")
            
        results = self.retriever.get_relevant_documents(query)
        return results[:k]
    
    def get_retriever(self):
        """
        Get the retriever object for use in RAG chains.
        
        Returns:
            Retriever object configured with MMR search
        """
        if not self.retriever:
            raise ValueError("Vector store not initialized")
        return self.retriever
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing vector store.
        
        Args:
            documents: List of Document objects to add
        """
        if not self.db:
            raise ValueError("Vector store not initialized")
            
        self.db.add_documents(documents)
        logger.info(f"Added {len(documents)} new documents to vector store")
