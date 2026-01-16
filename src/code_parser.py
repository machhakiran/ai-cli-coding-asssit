from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from typing import List
from langchain_core.documents import Document
import os


class CodeParser:
    """
    Parses code files using AST (Abstract Syntax Tree) to maintain semantic integrity.
    Unlike simple text splitters, this ensures functions and classes are not broken mid-way.
    """
    
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def load_repository(self, repo_path: str, file_extensions: List[str] = None) -> List[Document]:
        """
        Load code files from a repository using AST-aware parsing.
        
        Args:
            repo_path: Path to the code repository
            file_extensions: List of file extensions to process (e.g., ['.py', '.js'])
            
        Returns:
            List of Document objects containing parsed code chunks
        """
        if file_extensions is None:
            file_extensions = [".py"]
            
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
            
        language_map = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".ts": Language.TS,
            ".java": Language.JAVA,
            ".cpp": Language.CPP,
            ".go": Language.GO,
            ".rs": Language.RUST,
        }
        
        all_documents = []
        
        for ext in file_extensions:
            if ext not in language_map:
                print(f"Warning: {ext} not supported, skipping...")
                continue
                
            language = language_map[ext]
            
            try:
                # Manually walk and load to handle encoding errors better
                for root, _, files in os.walk(repo_path):
                    for file in files:
                        if file.endswith(ext):
                            file_path = os.path.join(root, file)
                            try:
                                from langchain_community.document_loaders import TextLoader
                                loader = TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
                                documents = loader.load()
                                
                                # Add language metadata for the splitter
                                for doc in documents:
                                    doc.metadata["language"] = language
                                    
                                all_documents.extend(documents)
                            except Exception as e:
                                print(f"Skipping {file_path} due to error: {e}")
                                continue
            except Exception as e:
                print(f"Error loading {ext} files: {e}")
                continue
        
        return all_documents
    
    def split_documents(self, documents: List[Document], language: Language = Language.PYTHON) -> List[Document]:
        """
        Split documents using AST-aware splitting to preserve code structure.
        
        Args:
            documents: List of Document objects to split
            language: Programming language for the splitter
            
        Returns:
            List of split Document chunks
        """
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        texts = splitter.split_documents(documents)
        print(f"Processed {len(texts)} semantic code chunks from {len(documents)} files.")
        
        return texts
    
    def parse_repository(self, repo_path: str, file_extensions: List[str] = None) -> List[Document]:
        """
        Complete parsing pipeline: load and split repository code.
        
        Args:
            repo_path: Path to the code repository
            file_extensions: List of file extensions to process
            
        Returns:
            List of semantically split code chunks
        """
        documents = self.load_repository(repo_path, file_extensions)
        
        if not documents:
            print("No documents loaded. Check repository path and file extensions.")
            return []
        
        primary_ext = file_extensions[0] if file_extensions else ".py"
        language_map = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".ts": Language.TS,
            ".java": Language.JAVA,
            ".cpp": Language.CPP,
            ".go": Language.GO,
            ".rs": Language.RUST,
        }
        
        language = language_map.get(primary_ext, Language.PYTHON)
        texts = self.split_documents(documents, language)
        
        return texts
