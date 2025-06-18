from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Tuple, Dict, Any

class SemanticSearch:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.original_documents = []  # store original JSON
        self.embedding_dim = None

    def _flatten_dict(self, d: Dict[str, Any], prefix: str = "") -> List[str]:
        lines = []
        for k, v in d.items():
            key = f"{prefix} {k}".strip()  # Use space instead of dot for better natural text
            if isinstance(v, dict):
                lines.extend(self._flatten_dict(v, key))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        lines.extend(self._flatten_dict(item, f"{key} {i}"))
                    else:
                        if item is not None:
                            lines.append(f"{key} {i}: {item}")
            else:
                if v is not None:
                    lines.append(f"{key}: {v}")
        return lines


    def embed_doc(self, documents: List[Dict[str, Any]]):
        self.original_documents = documents  # store JSONs
        flat_texts = ["\n".join(self._flatten_dict(doc)) for doc in documents]
        embeddings = self.model.encode(flat_texts).astype('float32')
        self.embedding_dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)

    def query(self, text: str, top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None:
            raise ValueError("Index is not initialized. Call embed_doc() first.")

        query_embedding = self.model.encode([text]).astype('float32')
        D, I = self.index.search(query_embedding, top_k)
        results = [(self.original_documents[i], float(D[0][rank])) for rank, i in enumerate(I[0])]
        return results
