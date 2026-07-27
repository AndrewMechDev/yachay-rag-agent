"""Ensambla el contexto final para el LLM a partir de los chunks recuperados."""

from typing import Any, Dict, List


def build_context(retrieved_chunks: List[Dict[str, Any]], max_tokens: int = 4000) -> str:
    """Ensambla el contexto con citación de fuente por cada fragmento, respetando un
    límite aproximado de tokens."""
    if not retrieved_chunks:
        return ""

    context_parts = []
    approx_tokens = 0

    for i, chunk in enumerate(retrieved_chunks, 1):
        meta = chunk["metadata"]
        source_info = (
            f"[Fuente {i}: {meta.get('source_file', 'desconocido')}"
            f" | Categoría: {meta.get('category', 'N/A')}"
            f" | Página: {meta.get('page', 'N/A')}"
            f" | Sección: {meta.get('section', 'N/A')}"
            f" | Score: {chunk.get('score', 'N/A')}]"
        )

        block = f"{source_info}\n{chunk['text']}\n"
        block_tokens = len(block.split()) * 1.3  # Aproximación tokens ≈ words × 1.3

        if approx_tokens + block_tokens > max_tokens:
            break

        context_parts.append(block)
        approx_tokens += block_tokens

    return "\n---\n".join(context_parts)


def extract_sources_for_ui(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extrae la información de fuentes para mostrar en la UI de Streamlit (Fase 5)."""
    sources = []
    for chunk in retrieved_chunks:
        meta = chunk["metadata"]
        sources.append(
            {
                "file": meta.get("source_file", "Desconocido"),
                "category": meta.get("category", "N/A"),
                "page": str(meta.get("page", "N/A")),
                "section": meta.get("section", "N/A"),
                "score": str(chunk.get("score", "N/A")),
                "chunk_id": meta.get("chunk_id", "N/A"),
                "preview": chunk["text"][:150] + "...",
            }
        )
    return sources
