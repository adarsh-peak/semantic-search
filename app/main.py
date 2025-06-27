from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from app.lib.elastic_search import ElasticsearchVectorStore  # SemanticSearch now handles flattening
from app.utils import row_to_text_full, parse_csv_to_summaries
from app.lib.llm import SemanticSearchLLM
import csv
import io
from app.lib.data_partioning import DataPartitioning

app = FastAPI()
search_engine = ElasticsearchVectorStore()  # Global instance
llm = SemanticSearchLLM()


@app.on_event("startup")
def load_index_on_startup():
    try:
        search_engine.init_index()
    except Exception as e:
        print(f"⚠️ Could not initialise index: {e}")

class EmbedDocumentInbound(BaseModel):
    data: List[dict]  # Accept multiple documents

@app.get("/")
def read_root():
    return {"message": "Semantic search API is up!"}

@app.post("/document")
async def embed_documents(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    texts = []
    rows = DataPartitioning.read_csv_file(file)
    for row in rows:
        texts.append(DataPartitioning.group_based_on_context(row))

    if not texts:
        raise HTTPException(status_code=422, detail="No valid rows found in the CSV.")
    

    search_engine.embed_doc_chunks([chunk for item in texts for chunk in item])
    return {"message": f"{len(texts)} rows embedded and indexed."}


@app.get("/search")
def query_documents(query: str = Query(..., description="Your search query"), top_k: int = 3):
    try:
        results = search_engine.query(query, top_k)
        print(results)
        context = [{"text": item.get('text'), "score": item.get('score')} for item in results]
        # results = llm.answer_question(query, [item.get('text') for item in context])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "query": query,
        # "results": results,
        "context": context
    }

@app.delete("/documents")
def delete_documents():
    try:
        search_engine.reset_index()
        return {"message": "✅ All documents deleted from Elasticsearch index."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to delete documents: {e}")
