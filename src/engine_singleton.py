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

La solucion en Windows es construir el RAGEngine en el hilo principal ANTES
de que Streamlit arranque su ScriptRunner (ver run_app.py). En Linux (Docker,
Streamlit Community Cloud) el bug no aplica -- WINHTTP.dll ni siquiera existe
ahi -- asi que get_engine() tambien soporta inicializacion perezosa (lazy) la
primera vez que se llama, para plataformas que ejecutan `streamlit run
app/app.py` directamente sin pasar por run_app.py.
"""
import threading
from typing import Optional

from src.rag_engine import RAGEngine

_engine: Optional[RAGEngine] = None
_lock = threading.Lock()


def init_engine() -> RAGEngine:
    """Construye el RAGEngine. En Windows debe llamarse desde el hilo
    principal (ver run_app.py); en Linux no importa desde donde se llame.

    Si el vector store esta vacio (primer arranque, o disco efimero en
    plataformas como Streamlit Community Cloud que no tienen un paso de build
    tipo Docker), corre la ingestion + indexacion automaticamente antes de
    construir el motor. `data/raw/` esta versionado en git, asi que esto
    siempre tiene datos para trabajar.
    """
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                from src.indexing.indexer import run_indexing_pipeline
                from src.indexing.vector_store import ChromaVectorStore
                from src.ingest.pipeline import run_ingestion_pipeline

                if ChromaVectorStore().count() == 0:
                    chunks = run_ingestion_pipeline()
                    run_indexing_pipeline(chunks)
                _engine = RAGEngine()
    return _engine


def get_engine() -> RAGEngine:
    """Devuelve el RAGEngine, construyendolo de forma perezosa si nadie lo
    pre-cargo todavia (seguro en Linux; en Windows preferir run_app.py)."""
    return init_engine()
