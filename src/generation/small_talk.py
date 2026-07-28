"""Detector de saludos/small talk: responde sin retrieval ni LLM.

Mensajes cortos tipo "hola" o "gracias" a veces superan SIMILARITY_THRESHOLD
por accidente (comparten vocabulario común con los documentos), pero no son
preguntas reales sobre el contenido. Interceptarlos aqui ahorra una llamada
al LLM y da una respuesta mas natural que el fallback generico de "no
encontré información".

Importante: NO usar palabras sueltas como "como" / "que" — disparan falsos
positivos en preguntas reales ("¿Cómo reporto un incidente P1?").
"""

import re
import unicodedata
from typing import Optional

from src.config import APP_NAME, BUSINESS_CATEGORIES

# Solo mensajes muy cortos: saludos reales. Preguntas tipicas del corpus
# tienen 5+ tokens y no deben entrar aqui.
_MAX_WORDS = 5

# Frases (no palabras sueltas). Se matchean sobre el texto normalizado.
_GREETING_PHRASES = (
    "hola",
    "buenas",
    "buen dia",
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "hey",
    "hi",
    "hello",
    "que tal",
    "como estas",
    "como esta",
    "como va",
    "empezar",
    "empiezo",
)
_THANKS_PHRASES = (
    "gracias",
    "muchas gracias",
    "mil gracias",
    "genial",
    "perfecto",
    "excelente",
)
_FAREWELL_PHRASES = (
    "chau",
    "adios",
    "bye",
    "nos vemos",
    "hasta luego",
    "hasta pronto",
)


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _word_count(normalized: str) -> int:
    return len(normalized.split()) if normalized else 0


def _matches_any(normalized: str, phrases: tuple) -> bool:
    """True si el mensaje es exactamente una frase, o la contiene como
    mensaje casi puro (sin mucho texto adicional)."""
    if not normalized:
        return False
    for phrase in phrases:
        if normalized == phrase:
            return True
        # "hola yachay" / "gracias !" ya normalizado
        if normalized.startswith(phrase + " ") and _word_count(normalized) <= _MAX_WORDS:
            return True
        if normalized.endswith(" " + phrase) and _word_count(normalized) <= _MAX_WORDS:
            return True
    return False


def detect_small_talk(query: str) -> Optional[str]:
    """Si `query` es un saludo/agradecimiento/despedida corto, devuelve la
    respuesta canned lista para mostrar. Si no, devuelve None (sigue el
    pipeline normal de retrieval + LLM)."""
    normalized = _normalize_text(query)
    if not normalized or _word_count(normalized) > _MAX_WORDS:
        return None

    # Si parece pregunta de contenido (verbos tipicos / "incidente" / etc.),
    # nunca tratarlo como small talk aunque contenga "como".
    content_markers = (
        "reporto", "reportar", "vacaciones", "gasto", "gastos", "incidente",
        "politica", "codigo", "etica", "onboarding", "remoto", "sla",
        "permiso", "reembolso", "privacidad", "datos", "proveedor",
        "compra", "caja", "chica", "interrupcion", "servicio",
    )
    if any(marker in normalized for marker in content_markers):
        return None

    if _matches_any(normalized, _THANKS_PHRASES):
        return "¡De nada! Si tienes otra pregunta sobre políticas o procesos internos, aquí estoy."

    if _matches_any(normalized, _FAREWELL_PHRASES):
        return "¡Hasta luego! Vuelve cuando necesites consultar algún documento interno."

    if _matches_any(normalized, _GREETING_PHRASES):
        areas = ", ".join(c["label"] for c in BUSINESS_CATEGORIES.values())
        return (
            f"¡Hola! Soy {APP_NAME}, tu asistente de conocimiento corporativo. "
            f"Puedo responder preguntas sobre {areas} usando los documentos internos de la empresa.\n\n"
            "Prueba con algo como *\"¿Cuántos días de vacaciones tengo?\"* o usa las sugerencias de abajo."
        )

    return None
