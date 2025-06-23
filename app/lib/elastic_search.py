from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import uuid
from app.configs.env import get_settings
from app.configs.constants import EmbeddingConstant, ElasticConstant

config = get_settings()

class ElasticsearchVectorStore:
    def __init__(
        self,
        index_name: str = ElasticConstant.index_name,
    ):
        self.index_name = index_name
        self.dims = EmbeddingConstant.dims
        self.es = Elasticsearch(
            f"http://{config.elastic_host}:{config.elastic_port}",
            headers={
                "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
                "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
            }
        )
        self.model = SentenceTransformer(EmbeddingConstant.model)

    def init_index(self):
        if self.es.indices.exists(index=self.index_name):
            print(f"Index '{self.index_name}' already exists.")
            return

        mapping = {
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": self.dims,
                        "index": True,
                        "similarity": "cosine",
                        "index_options": {
                            "type": "hnsw",
                            "m": 16,
                            "ef_construction": 100
                        }
                    }
                }
            }
        }

        self.es.indices.create(index=self.index_name, body=mapping)
        print(f"Index '{self.index_name}' created.")

    def embed_doc(self, texts: List[str]):
        for text in texts:
            embedding = self.model.encode(text).tolist()
            doc = {
                "text": text,
                "embedding": embedding
            }
            self.es.index(index=self.index_name, id=str(uuid.uuid4()), body=doc)

        print(f"Added {len(texts)} documents to '{self.index_name}'.")

    def query(self, query_text: str, k: int = 3, num_candidates: int = 100):
        query_vector = self.model.encode(query_text).tolist()
        body = {
            "knn": {
                "field": "embedding",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": num_candidates
            }
        }

        response = self.es.search(index=self.index_name, body=body)
        results = [
            {
                "text": hit["_source"]["text"],
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

        return results

    def reset_index(self):
        """
        Deletes the entire index (including mappings and data), then recreates it.
        """
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print(f"Index '{self.index_name}' deleted.")
        self.init_index()
