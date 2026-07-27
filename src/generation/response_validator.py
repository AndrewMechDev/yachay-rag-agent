"""Validación de respuestas y cálculo de un score de confianza."""

from typing import Any, Dict, List

from src.config import SIMILARITY_THRESHOLD

FALLBACK_INDICATORS = [
    "no encontré información",
    "no hay información suficiente",
    "no dispongo de",
    "no tengo información",
    "no se encontraron",
]

AREA_LABELS = {
    "rrhh": "Recursos Humanos (RRHH)",
    "financiero": "Finanzas",
    "legal": "el área Legal",
    "operacional": "Operaciones",
    "general": "el área correspondiente",
}


def validate_response(
    response: str,
    retrieved_chunks: List[Dict[str, Any]],
    threshold: float = SIMILARITY_THRESHOLD,
) -> Dict[str, Any]:
    """Valida la respuesta del LLM y calcula un score de confianza.

    Returns:
        {"response": str, "confidence": float, "fallback_triggered": bool, "sources_count": int}
    """
    if not retrieved_chunks:
        return {
            "response": generate_fallback_response("general"),
            "confidence": 0.0,
            "fallback_triggered": True,
            "sources_count": 0,
        }

    avg_score = sum(c.get("score", 0) for c in retrieved_chunks) / len(retrieved_chunks)
    max_score = max(c.get("score", 0) for c in retrieved_chunks)

    has_fallback = any(ind in response.lower() for ind in FALLBACK_INDICATORS)

    confidence = avg_score * 0.4 + max_score * 0.4 + (0.2 if not has_fallback else 0.0)
    confidence = min(1.0, max(0.0, confidence))

    return {
        "response": response,
        "confidence": round(confidence, 3),
        "fallback_triggered": has_fallback or confidence < threshold,
        "sources_count": len(retrieved_chunks),
    }


def generate_fallback_response(category: str = "general") -> str:
    """Genera respuesta de fallback con sugerencia de contacto por área."""
    area = AREA_LABELS.get(category, "el área correspondiente")
    return (
        f"No encontré información suficiente sobre este tema en los documentos disponibles.\n\n"
        f"Te sugiero contactar a **{area}** para obtener una respuesta precisa."
    )
