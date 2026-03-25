from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

class LongTermMemory:
    def __init__(self, db_path="memory_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(name="enigma_memory")

    def add(self, text: str, metadata: dict):
        """Add a document to long-term memory."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(hash(text))]
        )

    def query(self, query_text: str, n_results: int = 5):
        """Retrieve relevant past knowledge."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

# Global memory instance
memory = LongTermMemory()
