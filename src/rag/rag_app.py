"""
Simple RAG (Retrieval-Augmented Generation) helper.
- Uses local sentence-transformers for embeddings (all-MiniLM-L6-v2).
- In-memory vector store (numpy) with cosine similarity retrieval.
- Pluggable generator function; a Gemini-based generator skeleton is provided.

Notes:
- Do NOT hardcode any API keys. Place your Gemini key in the environment variable GEMINI_API_KEY.
- This module keeps generation calls isolated so you can replace the generator with any API.
"""

import os
from typing import List, Dict, Any, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


def load_embedder(model_name: str = "all-MiniLM-L6-v2") -> Any:
    if SentenceTransformer is None:
        raise RuntimeError(
            "sentence-transformers is not installed. Install with: pip install sentence-transformers"
        )
    return SentenceTransformer(model_name)


class SimpleRAG:
    def __init__(self, embedder=None):
        self.embedder = embedder or load_embedder()
        self.docs: List[str] = []
        self.embeddings: np.ndarray = np.zeros((0, self.embedder.get_sentence_embedding_dimension()))

    def index_documents(self, documents: List[str]):
        """Index a list of documents (replace existing index)."""
        self.docs = documents
        embeddings = self.embedder.encode(documents, convert_to_numpy=True)
        # normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings = embeddings / norms

    def add_documents(self, documents: List[str]):
        """Append new documents to the existing index."""
        new_embeddings = self.embedder.encode(documents, convert_to_numpy=True)
        norms = np.linalg.norm(new_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        new_embeddings = new_embeddings / norms
        if self.embeddings.size == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        self.docs.extend(documents)

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[int, float, str]]:
        """Retrieve top_k documents for the query. Returns list of (index, score, doc_text)."""
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-12)
        sims = (self.embeddings @ q_emb[0])
        top_idx = np.argsort(-sims)[:top_k]
        results = [(int(i), float(sims[i]), self.docs[i]) for i in top_idx]
        return results


# ---- Gemini generator skeleton ----
import requests


def gemini_generate(prompt: str, api_key: str = None, model: str = "text-bison-001") -> str:
    """Call Gemini/Google Generative API to generate a response.

    IMPORTANT: API endpoints and parameters for Gemini (Google Generative Models) may change.
    This function is a best-effort skeleton. Set your key in GEMINI_API_KEY and verify the
    endpoint/model name against the current Google Generative AI docs.

    Parameters:
        prompt: the full prompt text to send to the generative model
        api_key: optional, if None will read from environment variable GEMINI_API_KEY
        model: target model name (default example `text-bison-001`)

    Returns:
        generated text (string)
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment. Set it and retry.")

    # Example endpoint - CHECK your cloud provider docs and update accordingly.
    # Two common variants: (A) Google Cloud REST endpoint using API key, (B) HTTP with OAuth Bearer token.
    # Below is a generic REST example that may require adjustments for your account.
    endpoint = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generate"

    headers = {
        "Content-Type": "application/json",
        # If using API key in header (Bearer) — adjust if your setup requires different auth.
        "Authorization": f"Bearer {api_key}",
    }

    body = {
        "prompt": {"text": prompt},
        # other parameters (temperature, maxOutputTokens) can be added here
        "temperature": 0.2,
        "maxOutputTokens": 512,
    }

    try:
        resp = requests.post(endpoint, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # parsing will depend on the exact API response shape
        # Commonly generated text is under data['candidates'][0]['content'] or data['output'][0]['content']
        # We'll try a couple of common paths:
        if "candidates" in data and isinstance(data["candidates"], list) and data["candidates"]:
            return data["candidates"][0].get("content", "")
        if "output" in data and isinstance(data["output"], list) and data["output"]:
            # sometimes content is nested differently
            first = data["output"][0]
            if isinstance(first, dict) and "content" in first:
                return first["content"]
        # fallback: return full json string
        return json.dumps(data)
    except Exception as e:
        # surface the error so the caller can see what went wrong
        return f"[GENERATION ERROR] {str(e)}"
