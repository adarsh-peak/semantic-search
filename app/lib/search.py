from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Tuple, Any
import os
from app.configs.constants import EmbeddingConstant

class SemanticSearch:
    def __init__(self, model_name: str = EmbeddingConstant.model):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.original_documents: List[str] = []  # store plain text
        self.embedding_dim = None

    def embed_doc(self, documents: List[str]):
        embeddings = self.model.encode(documents).astype('float32')

        if self.index is None:
            self.embedding_dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.original_documents = []

        self.index.add(embeddings)
        self.original_documents.extend(documents)

    def query(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if self.index is None:
            raise ValueError("Index is not initialized. Call embed_doc() first.")

        query_embedding = self.model.encode([text]).astype('float32')
        D, I = self.index.search(query_embedding, top_k)
        print(D, I, flush=True)
        results = [(self.original_documents[i], float(D[0][rank])) for rank, i in enumerate(I[0])]
        return results

    def save(self, index_path: str = "index.faiss", docs_path: str = "documents.txt"):
        if self.index is not None:
            faiss.write_index(self.index, index_path)
        with open(docs_path, "w", encoding="utf-8") as f:
            for doc in self.original_documents:
                f.write(doc.strip().replace("\n", " ") + "\n")

    def load(self, index_path: str = "index.faiss", docs_path: str = "documents.txt"):
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        if os.path.exists(docs_path):
            with open(docs_path, "r", encoding="utf-8") as f:
                self.original_documents = [line.strip() for line in f]
