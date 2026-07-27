"""Contenedor del RAGEngine pre-inicializado en el hilo principal.

Por que existe este modulo (no fusionar con rag_engine.py):
En Windows, torch (MKL/OpenMP) y chromadb (OpenTelemetry/grpc) crashean con
STATUS_ACCESS_VIOLATION (0xC0000005 en WINHTTP.dll) si se inicializan
JUNTOS fuera del hilo principal del proceso. Confirmado por biseccion:
- scripts/ingest_documents.py (hilo principal): nunca crashea.
- app/app.py via `streamlit run` (hilo ScriptRunner, no es el principal):
  crashea ~2s despues de construir RAGEngine, siempre, con offset identico.
- Cargar solo el embedder o solo chromadb en Streamlit: no crashea.
- Cargar ambos en Streamlit con threads de OpenMP limitados a 1: sigue
  crasheando (descarta contencion de hilos; es un problema de inicializacion,
  no de concurrencia en ejecucion).

La solucion es construir el RAGEngine en el hilo principal ANTES de que
Streamlit arranque su ScriptRunner (ver run_app.py), y que app.py solo lea
esta instancia ya construida via get_engine(), sin volver a instanciar nada
pesado en el hilo de Streamlit.
"""
from typing import Optional

from src.rag_engine import RAGEngine

_engine: Optional[RAGEngine] = None


def init_engine() -> RAGEngine:
    """Construye el RAGEngine. Debe llamarse desde el hilo principal
    (ver run_app.py), nunca desde dentro de un script de Streamlit."""
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine


def get_engine() -> RAGEngine:
    """Devuelve el RAGEngine ya construido. Lanza si init_engine() no corrio antes."""
    if _engine is None:
        raise RuntimeError(
            "RAGEngine no inicializado. Ejecuta la app con `python run_app.py`, "
            "no con `streamlit run app/app.py` directamente (ver comentario en este archivo)."
        )
    return _engine
