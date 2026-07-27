"""RAG Engine: orquestador principal del pipeline pregunta → respuesta citada.

Depende solo de las interfaces (`Retriever` usa `VectorStore`; la generación usa
`LLMClient` vía `get_llm_client()`), nunca de `chromadb` u `openai` directamente
(yachay-buenas-practicas).
"""

import time
from typing import Any, Dict, Optional

from loguru import logger

from src.generation.llm_client import get_llm_client
from src.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from src.generation.response_validator import validate_response
from src.logging_config import log_interaction
from src.retrieval.context_builder import build_context, extract_sources_for_ui
from src.retrieval.reranker import rerank
from src.retrieval.retriever import Retriever


class RAGEngine:
    """Motor RAG principal de YACHAY."""

    def __init__(self):
        logger.info("Inicializando YACHAY RAG Engine...")
        self.retriever = Retriever()
        self.llm = get_llm_client()
        logger.info(f"RAG Engine listo (LLM: {type(self.llm).__name__}).")

    def ask(self, query: str, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Pipeline completo: pregunta → retrieval → rerank → contexto → LLM → validación.

        Returns:
            {"query", "response", "sources", "confidence", "fallback_triggered",
             "sources_count", "latency_ms"}
        """
        start = time.time()

        retrieved = self.retriever.retrieve(query=query, category_filter=category_filter)
        reranked = rerank(query=query, candidates=retrieved)

        context = build_context(reranked)
        sources = extract_sources_for_ui(reranked)

        user_prompt = build_user_prompt(query, context)
        raw_response = self.llm.generate(system_prompt=SYSTEM_PROMPT, user_message=user_prompt)

        validation = validate_response(raw_response, reranked)

        latency_ms = round((time.time() - start) * 1000, 1)

        result = {
            "query": query,
            "response": validation["response"],
            "sources": sources,
            "confidence": validation["confidence"],
            "fallback_triggered": validation["fallback_triggered"],
            "sources_count": validation["sources_count"],
            "latency_ms": latency_ms,
        }

        log_interaction(
            query=query,
            sources=sources,
            response=validation["response"],
            confidence=validation["confidence"],
            latency_ms=latency_ms,
        )

        return result
