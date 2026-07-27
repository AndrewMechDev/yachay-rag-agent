"""Detector de saludos/small talk: responde sin retrieval ni LLM.

Mensajes cortos tipo "hola" o "gracias" a veces superan SIMILARITY_THRESHOLD
por accidente (comparten vocabulario común con los documentos), pero no son
preguntas reales sobre el contenido. Interceptarlos aqui ahorra una llamada
al LLM y da una respuesta mas natural que el fallback generico de "no
encontré información".
"""

import re
import unicodedata
from typing import Optional

from src.config import APP_NAME, BUSINESS_CATEGORIES

_MAX_WORDS = 6

_GREETING_WORDS = {
    "hola", "buenas", "buenos", "buen", "dias", "tardes", "noches", "hey",
    "hi", "hello", "que", "tal", "como", "estas", "empezar", "empiezo",
}
_THANKS_WORDS = {"gracias", "genial", "perfecto", "excelente", "gracias!"}
_FAREWELL_WORDS = {"chau", "adios", "bye", "nos", "vemos", "hasta", "luego"}


def _normalize(text: str) -> list:
    text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()


def detect_small_talk(query: str) -> Optional[str]:
    """Si `query` es un saludo/agradecimiento/despedida corto, devuelve la
    respuesta canned lista para mostrar. Si no, devuelve None (sigue el
    pipeline normal de retrieval + LLM)."""
    words = _normalize(query)
    if not words or len(words) > _MAX_WORDS:
        return None

    word_set = set(words)

    if word_set & _THANKS_WORDS:
        return "¡De nada! Si tienes otra pregunta sobre políticas o procesos internos, aquí estoy."

    if word_set & _FAREWELL_WORDS:
        return "¡Hasta luego! Vuelve cuando necesites consultar algún documento interno."

    if word_set & _GREETING_WORDS:
        areas = ", ".join(c["label"] for c in BUSINESS_CATEGORIES.values())
        return (
            f"¡Hola! Soy {APP_NAME}, tu asistente de conocimiento corporativo. "
            f"Puedo responder preguntas sobre {areas} usando los documentos internos de la empresa.\n\n"
            "Prueba con algo como *\"¿Cuántos días de vacaciones tengo?\"* o usa las sugerencias de abajo."
        )

    return None
