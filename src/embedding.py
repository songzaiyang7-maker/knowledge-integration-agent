"""Embedding module using sentence-transformers (BGE-small-zh-v1.5)."""

import numpy as np
from src.config import EMBEDDING_MODEL

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def encode_texts(texts: list[str]) -> np.ndarray:
    """Encode a list of texts into embeddings.

    Returns:
        numpy array of shape (len(texts), dim)
    """
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings


def compute_similarity_matrix(embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
    """Compute cosine similarity matrix between two sets of embeddings.

    Returns:
        numpy array of shape (len(embeddings1), len(embeddings2))
    """
    # Already normalized, so dot product = cosine similarity
    return np.dot(embeddings1, embeddings2.T)


def find_similar_pairs(nodes1: list[dict], nodes2: list[dict], threshold: float = 0.85) -> list[tuple]:
    """Find pairs of similar nodes between two node lists based on name embedding.

    Args:
        nodes1: list of node dicts with "name" key
        nodes2: list of node dicts with "name" key
        threshold: cosine similarity threshold

    Returns:
        list of (idx1, idx2, similarity) tuples
    """
    names1 = [n["name"] for n in nodes1]
    names2 = [n["name"] for n in nodes2]

    emb1 = encode_texts(names1)
    emb2 = encode_texts(names2)

    sim_matrix = compute_similarity_matrix(emb1, emb2)

    pairs = []
    for i in range(len(nodes1)):
        for j in range(len(nodes2)):
            sim = float(sim_matrix[i][j])
            if sim >= threshold:
                pairs.append((i, j, sim))

    # Sort by similarity descending
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs
