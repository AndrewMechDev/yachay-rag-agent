"""Configuración de loguru: logging estructurado + trazabilidad de interacciones RAG."""

import sys

from loguru import logger

from src.config import LOG_FILE, LOG_LEVEL, SIMILARITY_THRESHOLD


def setup_logging():
    """Configura loguru: consola legible + archivo JSONL para evidencia de ejecución."""
    logger.remove()

    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | <cyan>{name}</cyan> | {message}",
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        LOG_FILE,
        level="INFO",
        format="{message}",
        serialize=True,
        rotation="10 MB",
        retention="7 days",
    )

    return logger


def log_interaction(query: str, sources: list, response: str, confidence: float, latency_ms: float):
    """Registra una interacción completa (pregunta → fuentes → respuesta) como evidencia trazable."""
    logger.info(
        "RAG_INTERACTION",
        query=query,
        sources_used=[
            {
                "file": s.get("file", "unknown"),
                "page": s.get("page", "N/A"),
                "category": s.get("category", "N/A"),
                "chunk_id": s.get("chunk_id", "N/A"),
                "score": s.get("score", 0.0),
            }
            for s in sources
        ],
        response_preview=response[:200],
        confidence_score=confidence,
        latency_ms=latency_ms,
        fallback_triggered=confidence < SIMILARITY_THRESHOLD,
    )
