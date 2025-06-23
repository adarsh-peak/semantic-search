from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from app.lib.elastic_search import ElasticsearchVectorStore  # SemanticSearch now handles flattening
from app.utils import pdf_to_text
from app.lib.llm import SemanticSearchLLM

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
async def embed_documents(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No PDF files uploaded.")

    texts = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Unsupported file: {file.filename}")
        try:
            text = pdf_to_text(file)
            if not text.strip():
                raise HTTPException(status_code=422, detail=f"No text extracted from {file.filename}")
            texts.append(text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract text from {file.filename}: {e}")

    search_engine.embed_doc(texts)
    return {"message": f"{len(texts)} PDF documents embedded and indexed."}

@app.get("/search")
def query_documents(query: str = Query(..., description="Your search query"), top_k: int = 3):
    try:
        results = search_engine.query(query, top_k)
        print(results)
        context = [item.get('text') for item in results]
        results = llm.answer_question(query, context)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "query": query,
        "results": results,
        "context": context
    }

@app.delete("/documents")
def delete_documents():
    try:
        search_engine.reset_index()
        return {"message": "✅ All documents deleted from Elasticsearch index."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to delete documents: {e}")
