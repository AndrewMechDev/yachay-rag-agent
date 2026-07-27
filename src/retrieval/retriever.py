"""Retriever: pregunta → embedding → búsqueda semántica → filtrado por umbral."""

from typing import Any, Dict, List, Optional

from loguru import logger

from src.config import SIMILARITY_THRESHOLD, TOP_K_RETRIEVAL
from src.indexing.embedder import LocalEmbedder
from src.indexing.vector_store import ChromaVectorStore, VectorStore


class Retriever:
    """Recupera los chunks más relevantes para una pregunta, ya filtrados por umbral."""

    def __init__(self, embedder: Optional[LocalEmbedder] = None, vector_store: Optional[VectorStore] = None):
        self.embedder = embedder or LocalEmbedder()
        self.vector_store = vector_store or ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        category_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Busca los chunks más relevantes. Aplica SIMILARITY_THRESHOLD ANTES de devolver
        resultados (yachay-rag-pipeline: el umbral se aplica antes de construir el contexto).

        Returns:
            Lista de dicts: {"text": str, "metadata": dict, "score": float, "rank": int}
        """
        query_embedding = self.embedder.embed_query(query)

        where = {"category": category_filter} if category_filter else None

        results = self.vector_store.query(query_embedding=query_embedding, n_results=top_k, where=where)

        retrieved = []
        if results and results.get("documents") and results["documents"][0]:
            for i, (doc, meta, dist) in enumerate(
                zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
            ):
                # Chroma retorna distancia coseno (0=idéntico, 2=opuesto) -> score de similitud (1=idéntico, 0=opuesto)
                score = 1.0 - (dist / 2.0)

                if score >= SIMILARITY_THRESHOLD:
                    retrieved.append({"text": doc, "metadata": meta, "score": round(score, 4), "rank": i + 1})

        logger.info(
            f"Retrieval: query='{query[:50]}...' → "
            f"{len(retrieved)}/{top_k} resultados sobre umbral (umbral={SIMILARITY_THRESHOLD})"
        )

        return retrieved
