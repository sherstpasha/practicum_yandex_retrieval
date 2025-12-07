import time
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List, Dict, Tuple
from tqdm import tqdm


class RetrievalSystem:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        reranker_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        self.reranker = CrossEncoder(reranker_name, device=self.device)
        self.index = None
        self.ids = []
        self.documents = []
        self.metadata = []

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        emb = self.model.encode(
            texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False
        )

        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        return emb.astype("float32")

    def build_index(
        self,
        documents: List[str],
        ids: List[str],
        metadata: List[Dict],
        batch_size: int = 32,
    ):
        self.documents = documents
        self.ids = ids
        self.metadata = metadata

        all_embeddings = []

        for i in tqdm(range(0, len(documents), batch_size), desc="Encoding documents"):
            batch = documents[i : i + batch_size]
            emb = self.encode(batch)
            all_embeddings.append(emb)

        all_embeddings = np.vstack(all_embeddings)

        dim = all_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(all_embeddings)

    def retrieve(
        self, query: str, top_k: int = 5, initial_k: int = 100, batch_size: int = 32
    ) -> Tuple[List[Dict], float, float, float]:
        t0 = time.perf_counter()
        query_emb = self.encode([query])
        t1 = time.perf_counter()

        scores, indices = self.index.search(query_emb, initial_k)
        t2 = time.perf_counter()

        candidates = []
        for pos, idx in enumerate(indices[0]):
            candidates.append(
                {
                    "id": self.ids[idx],
                    "score": float(scores[0][pos]),
                    "text": self.documents[idx],
                    "meta": self.metadata[idx],
                }
            )

        pairs = [(query, c["text"]) for c in candidates]
        rerank_scores = self.reranker.predict(pairs, batch_size=batch_size)
        t3 = time.perf_counter()

        ranked = sorted(
            zip(rerank_scores, candidates), key=lambda x: x[0], reverse=True
        )

        results = [
            {
                "id": cand["id"],
                "score": float(score),
                "text": cand["text"],
                "meta": cand["meta"],
            }
            for score, cand in ranked[:top_k]
        ]

        encode_time = t1 - t0
        search_time = t2 - t1
        rerank_time = t3 - t2

        return results, encode_time, search_time, rerank_time
