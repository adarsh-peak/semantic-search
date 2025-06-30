from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from app.lib.elastic_search import ElasticsearchVectorStore  # SemanticSearch now handles flattening
from app.utils import row_to_text_full, parse_csv_to_summaries, dict_to_text
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
        
    print("texts", texts)

    if not texts:
        raise HTTPException(status_code=422, detail="No valid rows found in the CSV.")
    

    search_engine.embed_doc_chunks([chunk for item in texts for chunk in item])
    return {"message": f"{len(texts)} rows embedded and indexed."}


@app.get("/search")
def query(user_query: str = Query(...), top_k: int = 3) -> Dict[str, Any]:
    try:
        parsed = llm.extract_query_and_filters(user_query)
        query_text = parsed["query_text"]
        es_filter = parsed.get("es_filter", {})
        
        print(query_text, es_filter)

        # ✅ Use hybrid_search_query instead of building query inline
        es_query = search_engine.hybrid_search_query(query_text, es_filter, k=top_k)

        response = search_engine.es.search(index=search_engine.index_name, body={"size": top_k, "query": es_query})

        results = [
            {
                "company_name": hit["_source"].get("company_name"),
                "chunk_type": hit["_source"].get("chunk_type"),
                "text": hit["_source"].get("text"),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
        
        llm_ans = llm.answer_question(user_query, [dict_to_text(item) for item in results])

        return {
            "query": user_query,
            "query_text": query_text,
            "llm_ans": llm_ans,
            "filters_applied": es_filter,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

@app.delete("/documents")
def delete_documents():
    try:
        search_engine.reset_index()
        return {"message": "✅ All documents deleted from Elasticsearch index."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to delete documents: {e}")
