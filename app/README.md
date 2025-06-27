# 🧠 Semantic Search with Elasticsearch and Mistral (via Ollama)

This project enables semantic search over documents using vector embeddings and a local LLM (Mistral) via [Ollama](https://ollama.com/). Documents are stored and indexed in Elasticsearch using dense vector search with HNSW.

---

## 🚀 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- [Ollama](https://ollama.com/download) installed locally

---

## 📦 Setup Instructions

### 1. 🔄 Start Mistral using Ollama
Make sure Ollama is running locally, then pull and start the model:

```bash
ollama run mistral
```

Keep this terminal running in the background — it hosts the LLM.

---

### 2. 🐳 Start Elasticsearch with Docker

From the project root, run:

```bash
docker compose up
```

This starts a single-node Elasticsearch instance with vector search enabled.

---

### 3. 🐍 Create and Activate Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

### 4. 📥 Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. 🔥 Launch the FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 API Endpoints

- `POST /document` – Upload and embed PDF documents
- `GET /search` – Search using a query and get answers from the LLM
- `DELETE /documents` – (Optional) Delete all documents from Elasticsearch

