import sys
print(f"Python Version: {sys.version}")

try:
    import chromadb
    print("SUCCESS: imported chromadb")
    print(f"ChromaDB Version: {chromadb.__version__}")
except ImportError as e:
    print(f"FAILURE: could not import chromadb: {e}")
except Exception as e:
    print(f"FAILURE: error importing chromadb: {e}")

try:
    from langchain_chroma import Chroma
    print("SUCCESS: imported langchain_chroma.Chroma")
except ImportError as e:
    print(f"FAILURE: could not import langchain_chroma: {e}")
except Exception as e:
    print(f"FAILURE: error importing langchain_chroma: {e}")
