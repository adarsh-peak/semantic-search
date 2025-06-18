from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from app.search import SemanticSearch  # SemanticSearch now handles flattening

app = FastAPI()
search_engine = SemanticSearch()  # Global instance


class EmbedDocumentInbound(BaseModel):
    data: List[dict]  # Accept multiple documents


@app.get("/")
def read_root():
    return {"message": "Semantic search API is up!"}


@app.post("/document")
def embed_documents(payload: EmbedDocumentInbound):
    if not payload.data:
        raise HTTPException(status_code=400, detail="No documents provided.")
    
    search_engine.embed_doc(payload.data)
    return {"message": f"{len(payload.data)} documents embedded and indexed."}


@app.get("/search")
def query_documents(query: str = Query(..., description="Your search query"), top_k: int = 3):
    try:
        results = search_engine.query(query, top_k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "query": query,
        "results": [
            {"document": doc, "distance": round(dist, 4)} for doc, dist in results
        ]
    }
