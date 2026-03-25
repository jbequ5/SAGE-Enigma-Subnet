from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import datetime

class LongTermMemory:
    def __init__(self, db_path="memory_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(name="enigma_memory")

    def add(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = str(datetime.datetime.now())
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(hash(text + str(datetime.datetime.now())))]
        )

    def query(self, query_text: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results.get('documents', [[]])[0]

# Global instance
memory = LongTermMemory()
