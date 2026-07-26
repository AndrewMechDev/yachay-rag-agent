"""Configuración centralizada: variables de entorno, paths y constantes del proyecto."""

from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# === OCI Generative AI ===
OCI_GENAI_API_KEY = os.getenv("OCI_GENAI_API_KEY", "")
OCI_REGION = os.getenv("OCI_REGION", "sa-saopaulo-1")
OCI_CHAT_MODEL = os.getenv("OCI_CHAT_MODEL", "meta.llama-3.3-70b-instruct")
OCI_GENAI_BASE_URL = os.getenv("OCI_GENAI_BASE_URL", "")

# === Embeddings ===
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# === Chroma ===
CHROMA_PERSIST_DIR = BASE_DIR / os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "yachay_docs")

# === Aplicación ===
APP_NAME = os.getenv("APP_NAME", "YACHAY")
APP_PORT = int(os.getenv("APP_PORT", "8501"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "./logs/yachay.jsonl")

# === Chunking ===
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))

# === Retrieval ===
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))

# === Datos ===
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# === Categorías de negocio (detectadas por carpeta padre en data/raw/) ===
BUSINESS_CATEGORIES = {
    "rrhh": {
        "label": "Recursos Humanos",
        "owner": "Gerencia de RRHH",
        "description": "Políticas de personal, beneficios, onboarding, vacaciones",
    },
    "financiero": {
        "label": "Financiero",
        "owner": "Gerencia de Finanzas",
        "description": "Políticas de gastos, presupuestos, reembolsos, reportes",
    },
    "legal": {
        "label": "Legal",
        "owner": "Gerencia Legal",
        "description": "Políticas de privacidad, contratos, compliance, normativa",
    },
    "operacional": {
        "label": "Operacional",
        "owner": "Gerencia de Operaciones",
        "description": "Manuales de procesos, SLAs, guías de incidentes, procedimientos",
    },
}

# === Formatos soportados por el pipeline de ingestión ===
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".md", ".csv", ".json", ".html", ".txt"}
