from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
from config import LLMConfig
from llm_factory import LLMFactory
import logging

logger = logging.getLogger(__name__)

class RAGChain:
    """
    RAG (Retrieval-Augmented Generation) chain for code assistance.
    Combines retrieved code context with LLM to provide accurate, context-aware answers.
    """
    
    def __init__(self, retriever, repo_map: str = "", config: LLMConfig = None):
        self.retriever = retriever
        self.repo_map = repo_map
        self.config = config or LLMConfig()
        self.chain = None
        self._build_chain()
        
    def _build_chain(self) -> None:
        """Build the RAG chain with appropriate prompts."""
        llm = LLMFactory.create_llm(self.config)
        
        repo_map_section = ""
        if self.repo_map:
            repo_map_section = f"\n\nREPOSITORY MAP:\n{self.repo_map}\n"
        
        prompt = ChatPromptTemplate.from_template(f"""You are a Senior Software Engineer assisting with a codebase.
Use the following pieces of retrieved context to answer the question.
If the context doesn't contain the answer, say "I don't have enough context."{repo_map_section}

CONTEXT FROM REPOSITORY:
{{context}}

USER QUESTION:
{{input}}

Instructions:
- Answer specifically using the class names, function names, and variable names found in the context
- Reference file paths when relevant
- If the repository map shows relevant files not in the context, mention them
- Provide code examples when appropriate
- Be precise and technical

Answer:""")
        
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        self.chain = create_retrieval_chain(self.retriever, combine_docs_chain)
        
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the codebase with a question.
        
        Args:
            question: User's question about the codebase
            
        Returns:
            Dictionary containing answer and source documents
        """
        if not self.chain:
            raise ValueError("RAG chain not initialized")
            
        response = self.chain.invoke({"input": question})
        return response
    
    def ask(self, question: str) -> str:
        """
        Simplified query method that returns just the answer.
        
        Args:
            question: User's question about the codebase
            
        Returns:
            Answer string
        """
        response = self.query(question)
        return response.get("answer", "No answer generated")
    
    def ask_with_sources(self, question: str) -> tuple:
        """
        Query and return both answer and source documents.
        
        Args:
            question: User's question about the codebase
            
        Returns:
            Tuple of (answer, source_documents)
        """
        response = self.query(question)
        answer = response.get("answer", "No answer generated")
        sources = response.get("context", [])
        
        return answer, sources
