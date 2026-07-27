"""Cliente LLM detrás de una interfaz mínima.

Interfaz explícita (yachay-buenas-practicas): junto a `vector_store.py`, es el
único otro punto de abstracción del proyecto, porque el LLM es una integración
externa reemplazable. `rag_engine.py` debe depender solo de `LLMClient` /
`get_llm_client()`, nunca importar `openai` directamente.

Mientras no haya cuenta OCI GenAI (OCI_GENAI_API_KEY vacío en .env), la factory
`get_llm_client()` devuelve `MockLLMClient`, que permite probar todo el pipeline
(retrieval → contexto → "generación" → validación) sin depender del LLM real.
Cuando se configure la API key, el mismo código empieza a usar OCIGenAIClient
sin tocar rag_engine.py.
"""

from abc import ABC, abstractmethod

from loguru import logger

from src.config import OCI_CHAT_MODEL, OCI_GENAI_API_KEY, OCI_GENAI_BASE_URL

# Valor placeholder que trae .env.example; si el usuario aún no lo reemplazó,
# se debe tratar como "no configurado" y caer a MockLLMClient.
_PLACEHOLDER_API_KEY = "tu_api_key_aqui"


def _has_real_api_key() -> bool:
    return bool(OCI_GENAI_API_KEY) and OCI_GENAI_API_KEY != _PLACEHOLDER_API_KEY


class LLMClient(ABC):
    """Interfaz mínima que `rag_engine.py` necesita de cualquier cliente LLM."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 1500,
    ) -> str:
        ...


class OCIGenAIClient(LLMClient):
    """Cliente para OCI Generative AI, consumido vía el endpoint OpenAI-compatible."""

    def __init__(self):
        from openai import OpenAI

        if not _has_real_api_key():
            raise ValueError(
                "OCI_GENAI_API_KEY no está configurada (o sigue en el valor placeholder). "
                "Edita .env y añade tu API Key real."
            )

        self.client = OpenAI(base_url=OCI_GENAI_BASE_URL, api_key=OCI_GENAI_API_KEY)
        self.model = OCI_CHAT_MODEL
        logger.info(f"OCI GenAI client inicializado: model={self.model}, base_url={OCI_GENAI_BASE_URL}")

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 1500,
    ) -> str:
        """Genera una respuesta con temperature baja (factual, no creativa)."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            logger.info(f"LLM response: {len(content)} chars, model={self.model}")
            return content

        except Exception as e:
            logger.error(f"Error en OCI GenAI: {e}")
            raise


class MockLLMClient(LLMClient):
    """Cliente simulado: NO genera texto real, solo confirma que retrieval y armado de
    contexto funcionan, devolviendo el contexto recuperado tal cual. Se usa automáticamente
    mientras no exista OCI_GENAI_API_KEY."""

    _NO_CONTEXT_MARKER = "No se encontraron fragmentos relevantes"

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 1500,
    ) -> str:
        logger.warning(
            "MockLLMClient activo (sin OCI_GENAI_API_KEY): esta respuesta NO fue generada por un LLM real."
        )

        if self._NO_CONTEXT_MARKER in user_message:
            return (
                "No encontré información suficiente sobre este tema en los documentos disponibles.\n\n"
                "Te sugiero contactar al área correspondiente para obtener una respuesta precisa."
            )

        marker = "CONTEXTO RECUPERADO DE DOCUMENTOS INTERNOS:"
        context = user_message.split(marker, 1)[-1]
        context = context.split("Responde la pregunta")[0].strip()
        preview = context[:1200] + ("..." if len(context) > 1200 else "")

        return (
            "[MODO MOCK — sin conexión a OCI GenAI, esto NO es una respuesta generada por un LLM]\n\n"
            "Se recuperaron los siguientes fragmentos relevantes para tu pregunta:\n\n"
            f"{preview}\n\n"
            "Configura OCI_GENAI_API_KEY en .env para obtener una respuesta real generada y citada."
        )


def get_llm_client() -> LLMClient:
    """Factory: OCIGenAIClient si hay API key real configurada; si no, MockLLMClient."""
    if _has_real_api_key():
        return OCIGenAIClient()
    logger.warning(
        "OCI_GENAI_API_KEY no configurada (o placeholder) — usando MockLLMClient (Fase 4 en modo mock)."
    )
    return MockLLMClient()
