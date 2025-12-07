import json
from fastapi import FastAPI
from pydantic import BaseModel
from retrieval_system import RetrievalSystem

ARXIV_METADATA_PATH = "..\\nlp_s3_project\\arxiv-metadata-s.json"

print("Loading metadata...")
with open(ARXIV_METADATA_PATH) as f:
    meta = json.load(f)

print("Initializing retriever...")
retriever = RetrievalSystem()

documents = [m["title"] + " " + m["abstract"] for m in meta]
ids = [m["id"] for m in meta]

retriever.build_index(documents, ids, meta)
print("RAG system ready.")

app = FastAPI()


class Query(BaseModel):
    query: str
    top_k: int = 5
    initial_k: int = 10


@app.get("/")
def root():
    return {"status": "ok", "message": "RAG server running"}


@app.post("/search")
def search(q: Query):
    results, enc, search, rer = retriever.retrieve(
        q.query, top_k=q.top_k, initial_k=q.initial_k
    )
    return {"results": results, "encode": enc, "search": search, "rerank": rer}
