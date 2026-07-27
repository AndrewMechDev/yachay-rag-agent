"""Wrapper de embeddings locales (BAAI/bge-m3, GPU si hay CUDA disponible)."""

from typing import List

from loguru import logger
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_DIMENSION, EMBEDDING_MODEL


class LocalEmbedder:
    """Genera embeddings con bge-m3 local. Mismo modelo para documentos y queries."""

    def __init__(self):
        logger.info(f"Cargando modelo de embeddings: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Modelo cargado. Dispositivo: {self.model.device}. Dimensión: {EMBEDDING_DIMENSION}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos (documentos/chunks)."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        # bge-m3 es Matryoshka: se puede truncar a EMBEDDING_DIMENSION sin re-entrenar.
        return [emb[:EMBEDDING_DIMENSION].tolist() for emb in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una pregunta de usuario."""
        embedding = self.model.encode(query, normalize_embeddings=True)
        return embedding[:EMBEDDING_DIMENSION].tolist()
