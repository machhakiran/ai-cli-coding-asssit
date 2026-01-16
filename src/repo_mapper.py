import os
import ast
from pathlib import Path
from typing import Dict, List, Set


class RepoMapper:
    """
    Creates a compressed tree structure of the entire codebase.
    This gives the LLM a global view of file structure and class definitions.
    Essential for large codebases (100k+ lines).
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.tree_structure = {}
        
    def extract_python_definitions(self, file_path: str) -> List[str]:
        """
        Extract class and function definitions from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of definition strings
        """
        definitions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    definitions.append(f"- class {node.name}")
                elif isinstance(node, ast.FunctionDef):
                    params = [arg.arg for arg in node.args.args]
                    definitions.append(f"- def {node.name}({', '.join(params)})")
                    
        except Exception as e:
            definitions.append(f"- [Parse error: {str(e)}]")
            
        return definitions
    
    def build_tree(self, extensions: Set[str] = None) -> str:
        """
        Build a tree structure of the repository with class and function definitions.
        
        Args:
            extensions: Set of file extensions to include (e.g., {'.py', '.js'})
            
        Returns:
            String representation of repository structure
        """
        if extensions is None:
            extensions = {'.py'}
            
        tree_lines = []
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            level = root.replace(self.repo_path, '').count(os.sep)
            indent = '  ' * level
            
            folder_name = os.path.basename(root) or self.repo_path
            tree_lines.append(f"{indent}{folder_name}/")
            
            sub_indent = '  ' * (level + 1)
            
            for file in sorted(files):
                if file.startswith('.'):
                    continue
                    
                file_ext = os.path.splitext(file)[1]
                if file_ext not in extensions:
                    continue
                    
                tree_lines.append(f"{sub_indent}{file}:")
                
                file_path = os.path.join(root, file)
                
                if file_ext == '.py':
                    definitions = self.extract_python_definitions(file_path)
                    for definition in definitions:
                        tree_lines.append(f"{sub_indent}  {definition}")
        
        return '\n'.join(tree_lines)
    
    def get_compact_map(self, extensions: Set[str] = None, max_lines: int = 100) -> str:
        """
        Get a compact version of the repository map, limited to important files.
        
        Args:
            extensions: Set of file extensions to include
            max_lines: Maximum number of lines in the output
            
        Returns:
            Compact string representation of repository structure
        """
        full_tree = self.build_tree(extensions)
        lines = full_tree.split('\n')
        
        if len(lines) <= max_lines:
            return full_tree
            
        important_lines = []
        for line in lines:
            if 'class ' in line or 'def ' in line or line.strip().endswith('/'):
                important_lines.append(line)
                if len(important_lines) >= max_lines:
                    break
        
        return '\n'.join(important_lines)
    
    def generate_context_map(self) -> str:
        """
        Generate a repository map suitable for inclusion in LLM context.
        
        Returns:
            Formatted repository map string
        """
        tree = self.build_tree()
        
        context = f"""REPOSITORY STRUCTURE:
{tree}

This map shows the file structure and main definitions in the codebase.
Use this to understand the overall architecture and locate relevant files.
"""
        return context
