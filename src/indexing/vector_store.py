"""Vector store con ChromaDB, detrás de una interfaz mínima.

Interfaz explícita (yachay-buenas-practicas): este es uno de los dos únicos
puntos del proyecto con abstracción, porque el vector store es una integración
externa reemplazable. `rag_engine.py` (Fase 4) debe depender solo de
`VectorStore`, nunca importar `chromadb` directamente.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from loguru import logger

from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR


class VectorStore(ABC):
    """Interfaz mínima que `rag_engine.py` necesita de cualquier vector store."""

    @abstractmethod
    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        ...

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    def count(self) -> int:
        ...

    @abstractmethod
    def reset(self) -> None:
        ...


class ChromaVectorStore(VectorStore):
    """Implementación de `VectorStore` sobre ChromaDB (HNSW nativo, persistente en disco)."""

    def __init__(self):
        logger.info(f"Inicializando Chroma (persist: {CHROMA_PERSIST_DIR})")
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:M": 16,
                "hnsw:construction_ef": 200,
                "description": "YACHAY corporate document embeddings",
            },
        )
        logger.info(f"Colección '{CHROMA_COLLECTION_NAME}': {self.collection.count()} documentos")

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        # Chroma no soporta metadatos anidados ni None; aplanar a tipos primitivos.
        flat_metadatas = []
        for m in metadatas:
            flat = {}
            for k, v in m.items():
                flat[k] = v if isinstance(v, (str, int, float, bool)) else str(v)
            flat_metadatas.append(flat)

        batch_size = 500
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=flat_metadatas[i : i + batch_size],
            )
        logger.info(f"Añadidos {len(ids)} documentos a Chroma")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        return self.collection.query(**kwargs)

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        """Elimina y recrea la colección (para re-indexación completa)."""
        self.client.delete_collection(CHROMA_COLLECTION_NAME)
        self.__init__()
        logger.warning("Colección reseteada")
