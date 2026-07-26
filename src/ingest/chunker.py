"""Chunking de textos con overlap y atribución de metadatos.

Usa CHUNK_SIZE/CHUNK_OVERLAP desde config.py (no hardcodear, ver skill
yachay-rag-pipeline).
"""

import hashlib
from typing import Any, Dict, List

from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(
    text: str,
    metadata: Dict[str, Any],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    category: str = "general",
) -> List[Dict[str, Any]]:
    """Divide texto en chunks con overlap, preservando metadatos de origen.

    Retorna una lista de dicts: {"chunk_id": str, "text": str, "metadata": dict}.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    chunks: List[Dict[str, Any]] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_body = " ".join(chunk_words)

        chunk_hash = hashlib.md5(chunk_body[:100].encode()).hexdigest()[:8]
        chunk_id = f"{metadata.get('source_file', 'unknown')}_{start}_{chunk_hash}"

        chunk_metadata = {
            **metadata,
            "category": category,
            "chunk_id": chunk_id,
            "chunk_index": len(chunks),
            "word_start": start,
            "word_end": min(end, len(words)),
            "total_words": len(chunk_words),
        }

        chunks.append({"chunk_id": chunk_id, "text": chunk_body, "metadata": chunk_metadata})

        step = max(1, chunk_size - chunk_overlap)
        start += step

    return chunks
