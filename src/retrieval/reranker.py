"""Reranker con cross-encoder local (BAAI/bge-reranker-v2-m3). Componente OPCIONAL.

Desactivado por defecto (RERANKER_ENABLED=False): el retriever base ya filtra por
umbral y ordena por score de Chroma, suficiente para el alcance de 2 días.
Se deja implementado para activarlo si da tiempo, sin romper el pipeline.
"""

from typing import Any, Dict, List

from loguru import logger

from src.config import TOP_K_RERANK

RERANKER_ENABLED = False

_reranker_model = None


def get_reranker():
    """Carga lazy del modelo de reranking (solo si RERANKER_ENABLED=True)."""
    global _reranker_model
    if _reranker_model is None:
        from sentence_transformers import CrossEncoder

        logger.info("Cargando reranker: BAAI/bge-reranker-v2-m3")
        _reranker_model = CrossEncoder("BAAI/bge-reranker-v2-m3")
    return _reranker_model


def rerank(query: str, candidates: List[Dict[str, Any]], top_k: int = TOP_K_RERANK) -> List[Dict[str, Any]]:
    """Re-ordena candidatos con un cross-encoder. Si está desactivado, retorna los primeros top_k."""
    if not RERANKER_ENABLED or not candidates:
        return candidates[:top_k]

    try:
        model = get_reranker()
        pairs = [(query, c["text"]) for c in candidates]
        scores = model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda x: x.get("rerank_score", 0), reverse=True)
        logger.info(f"Reranking: {len(candidates)} → top {top_k}")
        return reranked[:top_k]

    except Exception as e:
        logger.warning(f"Reranking falló, retornando candidatos originales: {e}")
        return candidates[:top_k]
