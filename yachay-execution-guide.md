# YACHAY — Guía de Ejecución Completa (Paso a Paso)

## Agente RAG Corporativo sobre OCI Generative AI

> **YACHAY** (quechua: *conocimiento, saber*) — Un agente de Retrieval-Augmented Generation que responde preguntas de colaboradores a partir de documentos internos corporativos, desplegado sobre Oracle Cloud Infrastructure.

---

## 0. IDENTIDAD DEL PROYECTO

| Campo | Valor |
|---|---|
| **Nombre** | YACHAY |
| **Slug / repo** | `yachay-rag-agent` |
| **Tagline** | "Conocimiento corporativo al alcance de una pregunta" |
| **Tipo** | Agente RAG corporativo multi-formato |
| **Lenguaje principal** | Python 3.11 |
| **Entregable** | Repositorio GitHub con README + app desplegada en OCI con evidencia |

---

## 1. STACK TÉCNICO DEFINITIVO (con versiones exactas)

### 1.1 Core Python

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **Runtime** | `python` | `3.11.9` | Última versión de la rama 3.11 con instalador de Windows disponible (desde 3.11.10 solo hay código fuente, sin .exe). Máxima compatibilidad con las libs del proyecto; 3.12/3.13/3.14 dan problemas con paquetes C (PyMuPDF, torch). Si ya tienes 3.12/3.14 instaladas, usa el `py launcher` (`py -3.11 -m venv venv`) para no interferir con ellas — ver sección 2.1. |
| **Gestor de deps** | `pip` + `requirements.txt` | — | Simple, sin poetry/pipenv para agilidad |
| **Entorno virtual** | `venv` | built-in | Aislamiento local |

### 1.2 LLM & Embeddings

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **Cliente LLM** | `openai` | `>=1.40.0` | SDK OpenAI apuntando a OCI GenAI (`base_url` custom) |
| **Modelo Chat** | `meta.llama-3.3-70b-instruct` | — | Vía OCI GenAI endpoint OpenAI-compatible |
| **Embeddings** | `sentence-transformers` | `>=3.0.0` | Para correr `BAAI/bge-m3` localmente |
| **Modelo Embeddings** | `BAAI/bge-m3` | latest | Multilingüe, 1024 dims, excelente en español |
| **Tokenizer** | `transformers` | `>=4.40.0` | Dependencia de sentence-transformers |
| **PyTorch** | `torch` | `>=2.2.0` (CPU) | Backend para embeddings locales |

### 1.3 Orquestación RAG

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **Framework** | `llama-index-core` | `>=0.11.0` | Orquestación RAG: ingestión, indexación, query |
| **Integración OpenAI** | `llama-index-llms-openai-like` | latest | Conectar LlamaIndex con endpoint OCI vía OpenAI SDK |
| **Integración embeddings** | `llama-index-embeddings-huggingface` | latest | Embeddings locales bge-m3 en LlamaIndex |
| **Vector store** | `llama-index-vector-stores-chroma` | latest | Integración Chroma con LlamaIndex |
| **Readers** | `llama-index-readers-file` | latest | Lectores multi-formato |

### 1.4 Vector Store

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **Base vectorial** | `chromadb` | `>=0.5.0` | Embebido, persistente en disco, HNSW nativo |

### 1.5 Extracción de documentos

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **PDF nativo** | `pymupdf` (fitz) | `>=1.24.0` | Extracción rápida de texto+estructura de PDFs |
| **PDF → Markdown** | `pymupdf4llm` | `>=0.0.10` | Salida Markdown ideal para RAG |
| **OCR** | `pytesseract` + `Pillow` | latest | PDFs escaneados. Requiere instalar el motor **Tesseract-OCR** aparte (no es un paquete pip): descarga el `.exe` desde `github.com/UB-Mannheim/tesseract/wiki` (NO desde `tesseract-ocr/tesseract`, que es solo código fuente sin instalador de Windows). Durante la instalación, expande **"Language data"** y marca **Spanish** además de English. Ruta típica: `C:\Program Files\Tesseract-OCR\tesseract.exe` — configúrala en `pytesseract.pytesseract.tesseract_cmd`. |
| **Word** | `python-docx` | `>=1.1.0` | Extracción preservando headings |
| **Excel** | `openpyxl` | `>=3.1.0` | Excel a texto estructurado |
| **PPT** | `python-pptx` | `>=0.6.23` | Slides + notas del orador |
| **CSV/JSON/HTML** | stdlib + `beautifulsoup4` | — | Parseo estándar |

### 1.6 Reranker (opcional, activar si da tiempo)

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **Reranker** | `sentence-transformers` | (ya instalado) | Cross-encoder `BAAI/bge-reranker-v2-m3` |

### 1.7 Interfaz

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **UI** | `streamlit` | `>=1.37.0` | Chat web con fuentes, feedback, historial |

### 1.8 Utilidades

| Componente | Paquete | Versión | Propósito |
|---|---|---|---|
| **Variables de entorno** | `python-dotenv` | `>=1.0.0` | Cargar `.env` localmente |
| **Logging estructurado** | `loguru` | `>=0.7.0` | Logs JSON para trazabilidad |
| **OCI SDK** | `oci` | `>=2.130.0` | (Opcional) Para Object Storage / Vault si se integra via SDK |

### 1.9 Infraestructura / Deploy

| Componente | Herramienta | Propósito |
|---|---|---|
| **Contenerización** | `Docker` + `Dockerfile` | Empaquetar la app |
| **Registry** | OCI Container Registry (OCIR) | Almacenar la imagen |
| **Cómputo** | OCI Compute (Ampere A1) o Container Instances | Ejecutar el contenedor |
| **Almacenamiento docs** | OCI Object Storage | Documentos fuente |
| **Secretos** | OCI Vault | API Key de GenAI |
| **Logs** | OCI Logging | Trazabilidad en nube |
| **LLM** | OCI Generative AI (Chat API) | Generación de respuestas |

---

## 2. ESTRUCTURA COMPLETA DEL REPOSITORIO

```
yachay-rag-agent/
│
├── README.md                          # README final (entregable principal)
├── .gitignore                         # Ignora .env, __pycache__, chroma_db/, models/
├── .env.example                       # Template de variables de entorno
├── requirements.txt                   # Dependencias Python con versiones
├── Dockerfile                         # Imagen Docker para deploy
├── docker-compose.yml                 # (Opcional) Compose para desarrollo local
├── Makefile                           # Comandos rápidos: setup, ingest, run, docker
│
├── docs/                              # Documentación adicional
│   ├── architecture.md                # Diagrama y explicación de arquitectura
│   ├── sources.md                     # Mapeo de fuentes, categorías y ownership
│   ├── deployment-oci.md              # Guía de deploy en OCI paso a paso
│   ├── trade-offs.md                  # Decisiones de diseño y justificaciones
│   └── screenshots/                   # Capturas de pantalla
│       ├── chat-response.png
│       ├── sources-display.png
│       ├── feedback-button.png
│       ├── oci-compute-running.png
│       ├── oci-logging-trace.png
│       └── oci-object-storage.png
│
├── data/                              # Documentos fuente para RAG
│   ├── raw/                           # Documentos originales organizados por categoría
│   │   ├── rrhh/                      # Recursos Humanos
│   │   │   ├── manual-empleado.pdf
│   │   │   ├── politica-vacaciones.docx
│   │   │   ├── beneficios-2024.xlsx
│   │   │   └── onboarding-presentacion.pptx
│   │   ├── financiero/                # Finanzas
│   │   │   ├── politica-gastos.pdf
│   │   │   ├── presupuesto-q3.xlsx
│   │   │   └── procedimiento-reembolsos.docx
│   │   ├── legal/                     # Legal y Cumplimiento
│   │   │   ├── politica-privacidad.pdf
│   │   │   ├── terminos-servicio.docx
│   │   │   └── compliance-checklist.md
│   │   └── operacional/              # Operaciones
│   │       ├── manual-procesos.pdf
│   │       ├── sla-proveedores.docx
│   │       └── guia-incidentes.md
│   ├── processed/                     # Chunks procesados (generados por el pipeline)
│   │   └── .gitkeep
│   └── catalog.json                   # Catálogo de documentos con metadatos
│
├── src/                               # Código fuente principal
│   ├── __init__.py
│   ├── config.py                      # Configuración centralizada (env vars, paths, constantes)
│   ├── ingest/                        # Módulo de ingestión de documentos
│   │   ├── __init__.py
│   │   ├── extractors.py             # Extractores por formato (PDF, DOCX, XLSX, PPTX, etc.)
│   │   ├── chunker.py                # Lógica de chunking con overlap + metadatos
│   │   ├── cleaner.py                # Limpieza de ruido (headers, footers, páginas en blanco)
│   │   └── pipeline.py              # Pipeline completo: extraer → limpiar → chunk → guardar
│   ├── indexing/                      # Módulo de indexación vectorial
│   │   ├── __init__.py
│   │   ├── embedder.py               # Wrapper de embeddings (bge-m3 local)
│   │   ├── vector_store.py           # Inicialización y operaciones sobre Chroma
│   │   └── indexer.py                # Pipeline: cargar chunks → embeddings → insertar en Chroma
│   ├── retrieval/                     # Módulo de recuperación
│   │   ├── __init__.py
│   │   ├── retriever.py              # Query → embedding → búsqueda semántica → filtro metadatos
│   │   ├── reranker.py               # (Opcional) Cross-encoder reranker
│   │   └── context_builder.py        # Ensamblar contexto final para el LLM
│   ├── generation/                    # Módulo de generación de respuestas
│   │   ├── __init__.py
│   │   ├── llm_client.py             # Cliente OCI GenAI vía OpenAI SDK
│   │   ├── prompts.py                # System prompt + templates anti-alucinación
│   │   └── response_validator.py     # Validación de confianza + fallback
│   ├── rag_engine.py                  # Orquestador principal: pregunta → respuesta citada
│   └── logging_config.py             # Configuración de loguru para trazabilidad
│
├── app/                               # Interfaz Streamlit
│   ├── app.py                         # Punto de entrada de Streamlit (streamlit run app/app.py)
│   ├── components/                    # Componentes UI reutilizables
│   │   ├── chat_message.py           # Renderizado de mensaje con fuentes
│   │   ├── feedback.py               # Botones 👍/👎 + persistencia
│   │   ├── sidebar.py                # Filtros por categoría, info del agente
│   │   └── source_card.py            # Card de fuente citada (archivo, página, fecha)
│   └── static/
│       └── logo.png                   # Logo del proyecto (opcional)
│
├── scripts/                           # Scripts de utilidad
│   ├── ingest_documents.py           # Script CLI para ejecutar la ingestión completa
│   ├── test_query.py                 # Script CLI para probar queries sin UI
│   ├── generate_sample_docs.py       # Genera documentos de ejemplo si no tienes reales
│   └── export_logs.py               # Exportar logs de trazabilidad
│
├── logs/                              # Logs locales de ejecución (en .gitignore)
│   └── .gitkeep
│
├── chroma_db/                         # Datos persistidos de Chroma (en .gitignore)
│   └── .gitkeep
│
├── tests/                             # Tests básicos
│   ├── __init__.py
│   ├── test_extractors.py            # Test de extracción por formato
│   ├── test_chunker.py               # Test de chunking
│   ├── test_retrieval.py             # Test de retrieval end-to-end
│   └── test_rag_engine.py            # Test del pipeline completo
│
└── oci/                               # Configuración específica de OCI para deploy
    ├── setup-guide.md                 # Pasos para configurar OCI
    ├── vault-setup.sh                 # Script para crear secreto en OCI Vault
    ├── compute-setup.sh               # Script para provisionar y configurar la VM
    ├── object-storage-upload.sh       # Script para subir docs a Object Storage
    └── logging-setup.sh               # Script para configurar OCI Logging
```

---

## 3. ARCHIVOS CLAVE — CONTENIDO DETALLADO

### 3.1 `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/

# Entorno virtual
venv/
.venv/
env/

# Variables de entorno (NUNCA subir la .env real)
.env

# Datos generados
chroma_db/
data/processed/*
!data/processed/.gitkeep

# Logs locales
logs/*
!logs/.gitkeep

# Modelos descargados (se bajan en runtime)
models/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker
*.tar
```

### 3.2 `.env.example`

```bash
# === OCI Generative AI ===
# API Key nativa de OCI GenAI (generada en Consola OCI → Analytics & AI → Generative AI → API Keys)
# IMPORTANTE: crear la key en la MISMA REGIÓN del modelo (ej. sa-saopaulo-1)
OCI_GENAI_API_KEY=tu_api_key_aqui

# Región OCI donde están los modelos de GenAI
OCI_REGION=sa-saopaulo-1

# Modelo de Chat (endpoint OpenAI-compatible; NO soporta Cohere)
OCI_CHAT_MODEL=meta.llama-3.3-70b-instruct

# Base URL del endpoint OpenAI-compatible de OCI GenAI
OCI_GENAI_BASE_URL=https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com/openai/v1

# === Embeddings (locales, no requieren API key) ===
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# === Chroma ===
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=yachay_docs

# === Aplicación ===
APP_NAME=YACHAY
APP_PORT=8501
LOG_LEVEL=INFO
LOG_FILE=./logs/yachay.jsonl

# === Chunking ===
CHUNK_SIZE=512
CHUNK_OVERLAP=80

# === Retrieval ===
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
SIMILARITY_THRESHOLD=0.35
```

### 3.3 `requirements.txt`

```txt
# === LLM Client (OCI GenAI vía OpenAI SDK) ===
openai>=1.40.0

# === Embeddings locales ===
sentence-transformers>=3.0.0
torch>=2.2.0  # CPU; para GPU: torch con CUDA

# === Framework RAG (LlamaIndex) ===
llama-index-core>=0.11.0
llama-index-llms-openai-like>=0.2.0
llama-index-embeddings-huggingface>=0.3.0
llama-index-vector-stores-chroma>=0.2.0
llama-index-readers-file>=0.2.0

# === Vector Store ===
chromadb>=0.5.0

# === Extracción de documentos ===
pymupdf>=1.24.0
pymupdf4llm>=0.0.10
pytesseract>=0.3.10
Pillow>=10.0.0
python-docx>=1.1.0
openpyxl>=3.1.0
python-pptx>=0.6.23
beautifulsoup4>=4.12.0

# === Interfaz ===
streamlit>=1.37.0

# === Utilidades ===
python-dotenv>=1.0.0
loguru>=0.7.0

# === OCI SDK (opcional, para integración directa con Object Storage/Vault) ===
# oci>=2.130.0
```

### 3.4 `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Dependencias del sistema para OCR y pymupdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descargar el modelo de embeddings durante el build (para no descargarlo en runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"

# Copiar el código fuente
COPY . .

# Puerto de Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "app/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
```

### 3.5 `Makefile`

```makefile
.PHONY: setup ingest run test docker-build docker-run clean

# === Desarrollo local ===

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ Entorno listo. Edita .env con tu API Key de OCI GenAI."

ingest:
	. venv/bin/activate && python scripts/ingest_documents.py

query:
	. venv/bin/activate && python scripts/test_query.py "$(Q)"

run:
	. venv/bin/activate && streamlit run app/app.py --server.port=8501

generate-docs:
	. venv/bin/activate && python scripts/generate_sample_docs.py

# === Docker ===

docker-build:
	docker build -t yachay-rag-agent:latest .

docker-run:
	docker run -d \
		--name yachay \
		-p 8501:8501 \
		--env-file .env \
		-v $(PWD)/data/raw:/app/data/raw:ro \
		-v $(PWD)/chroma_db:/app/chroma_db \
		-v $(PWD)/logs:/app/logs \
		yachay-rag-agent:latest

docker-stop:
	docker stop yachay && docker rm yachay

# === Tests ===

test:
	. venv/bin/activate && python -m pytest tests/ -v

# === Limpieza ===

clean:
	rm -rf chroma_db/
	rm -rf logs/*.jsonl
	rm -rf data/processed/*
	@echo "🧹 Limpieza completa."
```

---

## 4. CÓDIGO FUENTE — TODOS LOS ARCHIVOS

### 4.1 `src/config.py` — Configuración centralizada

```python
"""
YACHAY — Configuración centralizada.
Carga variables de entorno y define constantes del proyecto.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "yachay.jsonl"))

# === OCI Generative AI ===
OCI_GENAI_API_KEY = os.getenv("OCI_GENAI_API_KEY")
OCI_GENAI_BASE_URL = os.getenv(
    "OCI_GENAI_BASE_URL",
    "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com/openai/v1"
)
OCI_CHAT_MODEL = os.getenv("OCI_CHAT_MODEL", "meta.llama-3.3-70b-instruct")

# === Embeddings ===
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# === Chroma ===
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "yachay_docs")

# === Chunking ===
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))

# === Retrieval ===
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))

# === App ===
APP_NAME = os.getenv("APP_NAME", "YACHAY")
APP_PORT = int(os.getenv("APP_PORT", "8501"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# === Categorías de negocio ===
BUSINESS_CATEGORIES = {
    "rrhh": {
        "label": "Recursos Humanos",
        "owner": "Gerencia de RRHH",
        "description": "Políticas de personal, beneficios, onboarding, vacaciones"
    },
    "financiero": {
        "label": "Financiero",
        "owner": "Gerencia de Finanzas",
        "description": "Políticas de gastos, presupuestos, reembolsos, reportes"
    },
    "legal": {
        "label": "Legal",
        "owner": "Gerencia Legal",
        "description": "Políticas de privacidad, contratos, compliance, normativa"
    },
    "operacional": {
        "label": "Operacional",
        "owner": "Gerencia de Operaciones",
        "description": "Manuales de procesos, SLAs, guías de incidentes, procedimientos"
    }
}

# Formatos soportados
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".pptx", ".md", ".csv", ".json", ".html", ".txt"}
```

### 4.2 `src/logging_config.py` — Logging con trazabilidad

```python
"""
YACHAY — Configuración de logging con trazabilidad completa.
Cada interacción se registra: pregunta → documentos usados → respuesta.
"""
import sys
from loguru import logger
from src.config import LOG_FILE, LOG_LEVEL

def setup_logging():
    """Configura loguru para logging estructurado JSON."""
    # Remover handler por defecto
    logger.remove()

    # Consola (formato legible)
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | <cyan>{name}</cyan> | {message}"
    )

    # Archivo JSONL (para trazabilidad y evidencia)
    logger.add(
        LOG_FILE,
        level="INFO",
        format="{message}",
        serialize=True,  # Salida JSON
        rotation="10 MB",
        retention="7 days"
    )

    return logger


def log_interaction(query: str, sources: list, response: str, confidence: float, latency_ms: float):
    """
    Registra una interacción completa para trazabilidad.
    Este log es la EVIDENCIA de ejecución requerida por la etapa 9.
    """
    logger.info(
        "RAG_INTERACTION",
        query=query,
        sources_used=[{
            "file": s.get("file", "unknown"),
            "page": s.get("page", "N/A"),
            "category": s.get("category", "N/A"),
            "chunk_id": s.get("chunk_id", "N/A"),
            "score": s.get("score", 0.0)
        } for s in sources],
        response_preview=response[:200],
        confidence_score=confidence,
        latency_ms=latency_ms,
        fallback_triggered=confidence < 0.35
    )
```

### 4.3 `src/ingest/extractors.py` — Extractores por formato

```python
"""
YACHAY — Extractores de contenido por formato.
Cada extractor devuelve una lista de dicts con:
  {"text": str, "metadata": {"page": int, "section": str, ...}}
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger


def extract_pdf(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de PDF nativo usando pymupdf4llm (salida Markdown)."""
    import pymupdf4llm

    try:
        md_text = pymupdf4llm.to_markdown(str(file_path), page_chunks=True)
        results = []
        for page_data in md_text:
            results.append({
                "text": page_data["text"],
                "metadata": {
                    "page": page_data.get("metadata", {}).get("page", 0) + 1,
                    "format": "pdf",
                    "extraction_method": "pymupdf4llm"
                }
            })
        return results
    except Exception as e:
        logger.warning(f"pymupdf4llm falló para {file_path}, intentando OCR: {e}")
        return extract_pdf_ocr(file_path)


def extract_pdf_ocr(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de PDF escaneado usando OCR (Tesseract)."""
    import fitz  # pymupdf
    import pytesseract
    from PIL import Image
    import io

    doc = fitz.open(str(file_path))
    results = []

    for page_num, page in enumerate(doc):
        # Renderizar página como imagen
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang="spa+eng")

        if text.strip():
            results.append({
                "text": text,
                "metadata": {
                    "page": page_num + 1,
                    "format": "pdf_ocr",
                    "extraction_method": "tesseract"
                }
            })

    doc.close()
    return results


def extract_docx(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de Word preservando estructura de headings."""
    from docx import Document

    doc = Document(str(file_path))
    results = []
    current_section = "Inicio"

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detectar headings para secciones
        if para.style.name.startswith("Heading"):
            current_section = text

        results.append({
            "text": text,
            "metadata": {
                "section": current_section,
                "style": para.style.name,
                "format": "docx",
                "extraction_method": "python-docx"
            }
        })

    return results


def extract_xlsx(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae contenido de Excel como texto estructurado (hoja por hoja)."""
    from openpyxl import load_workbook

    wb = load_workbook(str(file_path), read_only=True, data_only=True)
    results = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue

        # Usar primera fila como headers si parece serlo
        headers = [str(cell) if cell else f"Col_{i}" for i, cell in enumerate(rows[0])]
        text_lines = [f"## Hoja: {sheet_name}", f"Columnas: {', '.join(headers)}", ""]

        for row in rows[1:]:
            row_text = " | ".join(
                f"{headers[i]}: {str(cell)}" for i, cell in enumerate(row) if cell is not None
            )
            if row_text.strip():
                text_lines.append(row_text)

        results.append({
            "text": "\n".join(text_lines),
            "metadata": {
                "sheet": sheet_name,
                "format": "xlsx",
                "extraction_method": "openpyxl"
            }
        })

    wb.close()
    return results


def extract_pptx(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de PowerPoint incluyendo notas del orador."""
    from pptx import Presentation

    prs = Presentation(str(file_path))
    results = []

    for slide_num, slide in enumerate(prs.slides, 1):
        texts = []

        # Texto de shapes
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                texts.append(shape.text.strip())

        # Notas del orador
        notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                texts.append(f"[Notas del orador]: {notes}")

        if texts:
            results.append({
                "text": "\n".join(texts),
                "metadata": {
                    "slide": slide_num,
                    "has_notes": bool(notes),
                    "format": "pptx",
                    "extraction_method": "python-pptx"
                }
            })

    return results


def extract_markdown(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de archivos Markdown."""
    text = file_path.read_text(encoding="utf-8")
    return [{
        "text": text,
        "metadata": {"format": "markdown", "extraction_method": "native"}
    }]


def extract_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae CSV como texto estructurado."""
    text_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        text_lines.append(f"Columnas: {', '.join(headers)}")
        for row in reader:
            row_text = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
            text_lines.append(row_text)

    return [{
        "text": "\n".join(text_lines),
        "metadata": {"format": "csv", "extraction_method": "csv.DictReader"}
    }]


def extract_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae JSON como texto legible."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    return [{
        "text": text,
        "metadata": {"format": "json", "extraction_method": "json.load"}
    }]


def extract_html(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de HTML eliminando tags."""
    from bs4 import BeautifulSoup

    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return [{
        "text": text,
        "metadata": {"format": "html", "extraction_method": "beautifulsoup4"}
    }]


def extract_text(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto plano."""
    text = file_path.read_text(encoding="utf-8")
    return [{
        "text": text,
        "metadata": {"format": "txt", "extraction_method": "native"}
    }]


# === Dispatcher ===
EXTRACTOR_MAP = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".xlsx": extract_xlsx,
    ".pptx": extract_pptx,
    ".md": extract_markdown,
    ".csv": extract_csv_file,
    ".json": extract_json_file,
    ".html": extract_html,
    ".txt": extract_text,
}


def extract_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae contenido de cualquier formato soportado."""
    ext = file_path.suffix.lower()
    extractor = EXTRACTOR_MAP.get(ext)
    if not extractor:
        logger.warning(f"Formato no soportado: {ext} ({file_path.name})")
        return []

    logger.info(f"Extrayendo: {file_path.name} (formato: {ext})")
    results = extractor(file_path)

    # Añadir metadatos comunes
    for r in results:
        r["metadata"]["source_file"] = file_path.name
        r["metadata"]["source_path"] = str(file_path)

    return results
```

### 4.4 `src/ingest/chunker.py` — Chunking con overlap y metadatos

```python
"""
YACHAY — Chunking de textos con overlap y atribución de metadatos.
"""
import hashlib
from typing import List, Dict, Any
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(
    text: str,
    metadata: Dict[str, Any],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    category: str = "general"
) -> List[Dict[str, Any]]:
    """
    Divide texto en chunks con overlap, preservando metadatos.

    Retorna lista de dicts:
      {"chunk_id": str, "text": str, "metadata": dict}
    """
    if not text or not text.strip():
        return []

    # Tokenización simple por palabras (robusto para español)
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        # Generar ID único del chunk
        chunk_hash = hashlib.md5(chunk_text[:100].encode()).hexdigest()[:8]
        chunk_id = f"{metadata.get('source_file', 'unknown')}_{start}_{chunk_hash}"

        chunk_metadata = {
            **metadata,
            "category": category,
            "chunk_id": chunk_id,
            "chunk_index": len(chunks),
            "word_start": start,
            "word_end": min(end, len(words)),
            "total_words": len(chunk_words)
        }

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "metadata": chunk_metadata
        })

        # Avanzar con overlap
        step = max(1, chunk_size - chunk_overlap)
        start += step

    return chunks
```

### 4.5 `src/ingest/cleaner.py` — Limpieza de ruido

```python
"""
YACHAY — Limpieza de ruido en textos extraídos.
"""
import re


def clean_text(text: str) -> str:
    """
    Limpia ruido común en documentos corporativos:
    - Múltiples saltos de línea
    - Headers/footers repetitivos
    - Caracteres de control
    - Espacios redundantes
    """
    if not text:
        return ""

    # Remover caracteres de control (excepto newline y tab)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Colapsar múltiples saltos de línea (>3 → 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Colapsar múltiples espacios
    text = re.sub(r' {2,}', ' ', text)

    # Remover líneas que solo tienen números (paginación)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Remover líneas de separación repetitivas (----, ====, etc.)
    text = re.sub(r'^[-=_*]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Trim por línea
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Trim final
    text = text.strip()

    return text
```

### 4.6 `src/ingest/pipeline.py` — Pipeline de ingestión completo

```python
"""
YACHAY — Pipeline de ingestión: escanear → extraer → limpiar → chunk → guardar.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger

from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR, BUSINESS_CATEGORIES, SUPPORTED_EXTENSIONS
from src.ingest.extractors import extract_file
from src.ingest.cleaner import clean_text
from src.ingest.chunker import chunk_text


def detect_category(file_path: Path) -> str:
    """Detecta la categoría de negocio basada en la carpeta padre."""
    parent = file_path.parent.name.lower()
    for cat_key in BUSINESS_CATEGORIES:
        if cat_key in parent:
            return cat_key
    return "general"


def scan_documents(base_dir: Path = DATA_RAW_DIR) -> List[Path]:
    """Escanea recursivamente el directorio de documentos."""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(base_dir.rglob(f"*{ext}"))
    # Ordenar para reproducibilidad
    files.sort()
    logger.info(f"Documentos encontrados: {len(files)}")
    return files


def build_catalog(files: List[Path]) -> List[Dict[str, Any]]:
    """Construye el catálogo de documentos con metadatos."""
    catalog = []
    for f in files:
        category = detect_category(f)
        entry = {
            "file": f.name,
            "path": str(f.relative_to(DATA_RAW_DIR)),
            "format": f.suffix.lower(),
            "category": category,
            "category_label": BUSINESS_CATEGORIES.get(category, {}).get("label", "General"),
            "owner": BUSINESS_CATEGORIES.get(category, {}).get("owner", "Sin asignar"),
            "size_kb": round(f.stat().st_size / 1024, 1),
            "last_modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "ingested_at": datetime.now().isoformat()
        }
        catalog.append(entry)
    return catalog


def run_ingestion_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline completo de ingestión.
    Retorna la lista de todos los chunks procesados con metadatos.
    """
    logger.info("=" * 60)
    logger.info("YACHAY — Iniciando pipeline de ingestión")
    logger.info("=" * 60)

    # 1. Escanear documentos
    files = scan_documents()
    if not files:
        logger.error(f"No se encontraron documentos en {DATA_RAW_DIR}")
        return []

    # 2. Construir y guardar catálogo
    catalog = build_catalog(files)
    catalog_path = DATA_RAW_DIR.parent / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    logger.info(f"Catálogo guardado: {catalog_path} ({len(catalog)} documentos)")

    # 3. Procesar cada archivo
    all_chunks = []
    stats = {"total_files": len(files), "success": 0, "failed": 0, "total_chunks": 0}

    for file_path in files:
        try:
            category = detect_category(file_path)
            logger.info(f"Procesando: {file_path.name} (categoría: {category})")

            # Extraer
            raw_segments = extract_file(file_path)

            # Limpiar + Chunk cada segmento
            for segment in raw_segments:
                cleaned = clean_text(segment["text"])
                if len(cleaned.split()) < 10:  # Descartar chunks muy cortos
                    continue

                chunks = chunk_text(
                    text=cleaned,
                    metadata=segment["metadata"],
                    category=category
                )
                all_chunks.extend(chunks)

            stats["success"] += 1
            logger.info(f"  → {len(raw_segments)} segmentos extraídos")

        except Exception as e:
            stats["failed"] += 1
            logger.error(f"Error procesando {file_path.name}: {e}")

    stats["total_chunks"] = len(all_chunks)

    # 4. Guardar chunks procesados
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chunks_path = DATA_PROCESSED_DIR / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    logger.info("=" * 60)
    logger.info(f"Ingestión completa: {stats}")
    logger.info(f"Chunks guardados: {chunks_path}")
    logger.info("=" * 60)

    return all_chunks
```

### 4.7 `src/indexing/embedder.py` — Wrapper de embeddings

```python
"""
YACHAY — Wrapper de embeddings locales (BAAI/bge-m3).
"""
from sentence_transformers import SentenceTransformer
from typing import List
from loguru import logger
from src.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION


class LocalEmbedder:
    """Genera embeddings con bge-m3 local. Mismo modelo para docs y queries."""

    def __init__(self):
        logger.info(f"Cargando modelo de embeddings: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Modelo cargado. Dimensión: {EMBEDDING_DIMENSION}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32
        )
        # Truncar a la dimensión deseada (Matryoshka)
        return [emb[:EMBEDDING_DIMENSION].tolist() for emb in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Genera embedding para una query."""
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )
        return embedding[:EMBEDDING_DIMENSION].tolist()
```

### 4.8 `src/indexing/vector_store.py` — Chroma

```python
"""
YACHAY — Vector Store con ChromaDB (HNSW nativo, persistente en disco).
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from loguru import logger
from src.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, EMBEDDING_DIMENSION


class ChromaVectorStore:
    """Wrapper sobre ChromaDB para YACHAY."""

    def __init__(self):
        logger.info(f"Inicializando Chroma (persist: {CHROMA_PERSIST_DIR})")
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",  # Similitud coseno
                "hnsw:M": 16,
                "hnsw:construction_ef": 200,
                "description": "YACHAY corporate document embeddings"
            }
        )
        logger.info(f"Colección '{CHROMA_COLLECTION_NAME}': {self.collection.count()} documentos")

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """Añade documentos al vector store."""
        # Chroma no soporta metadatos anidados; aplanar
        flat_metadatas = []
        for m in metadatas:
            flat = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)):
                    flat[k] = v
                else:
                    flat[k] = str(v)
            flat_metadatas.append(flat)

        # Insertar en batches de 500
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=flat_metadatas[i:i+batch_size]
            )
        logger.info(f"Añadidos {len(ids)} documentos a Chroma")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Busca los documentos más similares."""
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)
        return results

    def count(self) -> int:
        """Retorna el número de documentos indexados."""
        return self.collection.count()

    def reset(self):
        """Elimina y recrea la colección (para re-indexación)."""
        self.client.delete_collection(CHROMA_COLLECTION_NAME)
        self.__init__()
        logger.warning("Colección reseteada")
```

### 4.9 `src/indexing/indexer.py` — Pipeline de indexación

```python
"""
YACHAY — Pipeline de indexación: chunks → embeddings → Chroma.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from src.config import DATA_PROCESSED_DIR
from src.indexing.embedder import LocalEmbedder
from src.indexing.vector_store import ChromaVectorStore


def run_indexing_pipeline(chunks: List[Dict[str, Any]] = None):
    """
    Indexa todos los chunks en el vector store.
    Si no se pasan chunks, los carga del archivo procesado.
    """
    logger.info("=" * 60)
    logger.info("YACHAY — Iniciando pipeline de indexación")
    logger.info("=" * 60)

    # Cargar chunks si no se pasan directamente
    if chunks is None:
        chunks_path = DATA_PROCESSED_DIR / "chunks.json"
        if not chunks_path.exists():
            logger.error("No hay chunks procesados. Ejecuta primero la ingestión.")
            return
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

    if not chunks:
        logger.error("No hay chunks para indexar.")
        return

    logger.info(f"Chunks a indexar: {len(chunks)}")

    # Inicializar embedder y vector store
    embedder = LocalEmbedder()
    vector_store = ChromaVectorStore()

    # Preparar datos
    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Generar embeddings
    logger.info("Generando embeddings (esto puede tomar unos minutos)...")
    embeddings = embedder.embed_texts(texts)
    logger.info(f"Embeddings generados: {len(embeddings)} vectores de dim {len(embeddings[0])}")

    # Insertar en Chroma
    vector_store.add_documents(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    logger.info(f"Indexación completa. Total en vector store: {vector_store.count()}")
```

### 4.10 `src/retrieval/retriever.py` — Búsqueda semántica

```python
"""
YACHAY — Retriever: query → embedding → búsqueda semántica → filtrado.
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from src.config import TOP_K_RETRIEVAL, SIMILARITY_THRESHOLD
from src.indexing.embedder import LocalEmbedder
from src.indexing.vector_store import ChromaVectorStore


class Retriever:
    """Recupera los chunks más relevantes para una pregunta."""

    def __init__(self):
        self.embedder = LocalEmbedder()
        self.vector_store = ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca los chunks más relevantes para la query.

        Returns:
            Lista de dicts con: text, metadata, score (0-1, mayor=mejor)
        """
        # 1. Embedding de la query
        query_embedding = self.embedder.embed_query(query)

        # 2. Filtro por metadatos (opcional)
        where = None
        if category_filter:
            where = {"category": category_filter}

        # 3. Búsqueda semántica en Chroma
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where
        )

        # 4. Formatear resultados
        retrieved = []
        if results and results["documents"] and results["documents"][0]:
            for i, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # Chroma retorna distancia coseno (0=idéntico, 2=opuesto)
                # Convertir a score de similitud (1=idéntico, 0=opuesto)
                score = 1.0 - (dist / 2.0)

                if score >= SIMILARITY_THRESHOLD:
                    retrieved.append({
                        "text": doc,
                        "metadata": meta,
                        "score": round(score, 4),
                        "rank": i + 1
                    })

        logger.info(
            f"Retrieval: query='{query[:50]}...' → "
            f"{len(retrieved)}/{top_k} resultados (umbral={SIMILARITY_THRESHOLD})"
        )

        return retrieved
```

### 4.11 `src/retrieval/reranker.py` — Reranker (opcional)

```python
"""
YACHAY — Reranker con cross-encoder local (BAAI/bge-reranker-v2-m3).
Componente OPCIONAL — si no da tiempo, el retriever base ya funciona.
"""
from typing import List, Dict, Any
from loguru import logger
from src.config import TOP_K_RERANK

# Flag para activar/desactivar sin romper el pipeline
RERANKER_ENABLED = False

_reranker_model = None


def get_reranker():
    """Carga lazy del modelo de reranking."""
    global _reranker_model
    if _reranker_model is None:
        from sentence_transformers import CrossEncoder
        logger.info("Cargando reranker: BAAI/bge-reranker-v2-m3")
        _reranker_model = CrossEncoder("BAAI/bge-reranker-v2-m3")
    return _reranker_model


def rerank(query: str, candidates: List[Dict[str, Any]], top_k: int = TOP_K_RERANK) -> List[Dict[str, Any]]:
    """
    Re-ordena los candidatos usando un cross-encoder.
    Si RERANKER_ENABLED es False, retorna los primeros top_k sin re-ordenar.
    """
    if not RERANKER_ENABLED or not candidates:
        return candidates[:top_k]

    try:
        model = get_reranker()
        pairs = [(query, c["text"]) for c in candidates]
        scores = model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda x: x.get("rerank_score", 0), reverse=True)
        logger.info(f"Reranking: {len(candidates)} → top {top_k}")
        return reranked[:top_k]

    except Exception as e:
        logger.warning(f"Reranking falló, retornando candidatos originales: {e}")
        return candidates[:top_k]
```

### 4.12 `src/retrieval/context_builder.py` — Ensamblaje de contexto

```python
"""
YACHAY — Ensambla el contexto final para el LLM a partir de los chunks recuperados.
"""
from typing import List, Dict, Any


def build_context(retrieved_chunks: List[Dict[str, Any]], max_tokens: int = 4000) -> str:
    """
    Ensambla el contexto con citación de fuente por cada fragmento.
    Respeta un límite aproximado de tokens.
    """
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
    """
    Extrae la información de fuentes para mostrar en la UI de Streamlit.
    """
    sources = []
    for chunk in retrieved_chunks:
        meta = chunk["metadata"]
        sources.append({
            "file": meta.get("source_file", "Desconocido"),
            "category": meta.get("category", "N/A"),
            "page": str(meta.get("page", "N/A")),
            "section": meta.get("section", "N/A"),
            "score": str(chunk.get("score", "N/A")),
            "chunk_id": meta.get("chunk_id", "N/A"),
            "preview": chunk["text"][:150] + "..."
        })
    return sources
```

### 4.13 `src/generation/llm_client.py` — Cliente OCI GenAI

```python
"""
YACHAY — Cliente LLM vía OCI Generative AI (endpoint OpenAI-compatible).
"""
from openai import OpenAI
from loguru import logger
from src.config import OCI_GENAI_API_KEY, OCI_GENAI_BASE_URL, OCI_CHAT_MODEL


class OCIGenAIClient:
    """Cliente para OCI Generative AI consumido vía OpenAI SDK."""

    def __init__(self):
        if not OCI_GENAI_API_KEY:
            raise ValueError(
                "OCI_GENAI_API_KEY no está configurada. "
                "Copia .env.example a .env y añade tu API Key."
            )

        self.client = OpenAI(
            base_url=OCI_GENAI_BASE_URL,
            api_key=OCI_GENAI_API_KEY,
        )
        self.model = OCI_CHAT_MODEL
        logger.info(f"OCI GenAI client inicializado: model={self.model}, base_url={OCI_GENAI_BASE_URL}")

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 1500
    ) -> str:
        """
        Genera una respuesta usando el Chat API de OCI GenAI.
        temperature baja (0.1) para respuestas factuales, no creativas.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
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
```

### 4.14 `src/generation/prompts.py` — System prompt anti-alucinación

```python
"""
YACHAY — Prompts del sistema con técnicas anti-alucinación.
"""

SYSTEM_PROMPT = """Eres YACHAY, un asistente de conocimiento corporativo que responde preguntas de colaboradores usando EXCLUSIVAMENTE la información proporcionada en el contexto.

## REGLAS ESTRICTAS:

1. **SOLO USA EL CONTEXTO**: Responde ÚNICAMENTE con información que aparezca explícitamente en los fragmentos proporcionados. NO uses conocimiento externo, suposiciones, ni inventes datos.

2. **CITA LA FUENTE**: Cada afirmación debe indicar de qué fuente proviene, usando el formato:
   📄 *[nombre_archivo | página/sección | categoría]*

3. **SI NO HAY INFORMACIÓN SUFICIENTE**: Responde EXACTAMENTE:
   "No encontré información suficiente sobre este tema en los documentos disponibles.
   Te sugiero contactar al área de [área responsable] para obtener una respuesta precisa."

4. **NO ADIVINES**: Si el contexto es ambiguo o incompleto, dilo explícitamente. Nunca rellenes con suposiciones.

5. **IDIOMA**: Responde siempre en español, de forma clara y profesional.

6. **FORMATO**: Usa viñetas o párrafos cortos para facilitar la lectura. Sé conciso pero completo.

## PROCESO DE RESPUESTA:
1. Lee todos los fragmentos del contexto
2. Identifica los fragmentos relevantes a la pregunta
3. Formula la respuesta SOLO con esos fragmentos
4. Añade la citación de fuente por cada punto
5. Si ningún fragmento es relevante, aplica la regla 3 (fallback)
"""


def build_user_prompt(query: str, context: str) -> str:
    """Construye el mensaje del usuario con contexto para el LLM."""
    if not context:
        return f"""Pregunta del colaborador: {query}

CONTEXTO DISPONIBLE: No se encontraron fragmentos relevantes.

Aplica la regla de fallback: indica que no encontraste información suficiente y sugiere contactar al área responsable."""

    return f"""Pregunta del colaborador: {query}

CONTEXTO RECUPERADO DE DOCUMENTOS INTERNOS:
{context}

Responde la pregunta del colaborador usando SOLO el contexto anterior. Cita las fuentes."""
```

### 4.15 `src/generation/response_validator.py` — Validación

```python
"""
YACHAY — Validación de respuestas y detección de confianza.
"""
from typing import Dict, Any, List


def validate_response(
    response: str,
    retrieved_chunks: List[Dict[str, Any]],
    threshold: float = 0.35
) -> Dict[str, Any]:
    """
    Valida la respuesta del LLM y calcula un score de confianza.

    Returns:
        {"response": str, "confidence": float, "fallback_triggered": bool, "sources_count": int}
    """
    # Score de confianza basado en:
    # 1. Cantidad de chunks recuperados
    # 2. Scores de similitud promedio
    # 3. Presencia de indicadores de fallback en la respuesta

    if not retrieved_chunks:
        return {
            "response": generate_fallback_response("general"),
            "confidence": 0.0,
            "fallback_triggered": True,
            "sources_count": 0
        }

    avg_score = sum(c.get("score", 0) for c in retrieved_chunks) / len(retrieved_chunks)
    max_score = max(c.get("score", 0) for c in retrieved_chunks)

    # Indicadores de baja confianza
    fallback_indicators = [
        "no encontré información",
        "no hay información suficiente",
        "no dispongo de",
        "no tengo información",
        "no se encontraron",
    ]
    has_fallback = any(ind in response.lower() for ind in fallback_indicators)

    # Calcular confianza compuesta
    confidence = (avg_score * 0.4 + max_score * 0.4 + (0.2 if not has_fallback else 0.0))
    confidence = min(1.0, max(0.0, confidence))

    return {
        "response": response,
        "confidence": round(confidence, 3),
        "fallback_triggered": has_fallback or confidence < threshold,
        "sources_count": len(retrieved_chunks)
    }


def generate_fallback_response(category: str = "general") -> str:
    """Genera respuesta de fallback con sugerencia de contacto."""
    area_map = {
        "rrhh": "Recursos Humanos (RRHH)",
        "financiero": "Finanzas",
        "legal": "el área Legal",
        "operacional": "Operaciones",
        "general": "el área correspondiente"
    }
    area = area_map.get(category, "el área correspondiente")

    return (
        f"No encontré información suficiente sobre este tema en los documentos disponibles.\n\n"
        f"Te sugiero contactar a **{area}** para obtener una respuesta precisa."
    )
```

### 4.16 `src/rag_engine.py` — Orquestador principal

```python
"""
YACHAY — RAG Engine: orquestador principal del pipeline pregunta → respuesta.
"""
import time
from typing import Dict, Any, Optional
from loguru import logger

from src.retrieval.retriever import Retriever
from src.retrieval.reranker import rerank
from src.retrieval.context_builder import build_context, extract_sources_for_ui
from src.generation.llm_client import OCIGenAIClient
from src.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from src.generation.response_validator import validate_response
from src.logging_config import log_interaction


class RAGEngine:
    """Motor RAG principal de YACHAY."""

    def __init__(self):
        logger.info("Inicializando YACHAY RAG Engine...")
        self.retriever = Retriever()
        self.llm = OCIGenAIClient()
        logger.info("RAG Engine listo.")

    def ask(
        self,
        query: str,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Pipeline completo: pregunta → retrieval → rerank → contexto → LLM → validación.

        Returns:
            {
                "query": str,
                "response": str,
                "sources": [{"file", "page", "category", "score", "preview"}],
                "confidence": float,
                "fallback_triggered": bool,
                "latency_ms": float
            }
        """
        start = time.time()

        # 1. Recuperar chunks relevantes
        retrieved = self.retriever.retrieve(
            query=query,
            category_filter=category_filter
        )

        # 2. Reranking (opcional, depende de RERANKER_ENABLED)
        reranked = rerank(query=query, candidates=retrieved)

        # 3. Construir contexto
        context = build_context(reranked)
        sources = extract_sources_for_ui(reranked)

        # 4. Generar respuesta con el LLM
        user_prompt = build_user_prompt(query, context)
        raw_response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_prompt
        )

        # 5. Validar respuesta
        validation = validate_response(raw_response, reranked)

        # 6. Calcular latencia
        latency_ms = round((time.time() - start) * 1000, 1)

        result = {
            "query": query,
            "response": validation["response"],
            "sources": sources,
            "confidence": validation["confidence"],
            "fallback_triggered": validation["fallback_triggered"],
            "sources_count": validation["sources_count"],
            "latency_ms": latency_ms
        }

        # 7. Registrar interacción (trazabilidad — etapa 9)
        log_interaction(
            query=query,
            sources=sources,
            response=validation["response"],
            confidence=validation["confidence"],
            latency_ms=latency_ms
        )

        return result
```

### 4.17 `app/app.py` — Interfaz Streamlit

```python
"""
YACHAY — Interfaz de chat con Streamlit.
Cumple: indicación de agente IA, fuentes, feedback, historial por sesión.
"""
import streamlit as st
from datetime import datetime
import json
from pathlib import Path

from src.rag_engine import RAGEngine
from src.config import APP_NAME, BUSINESS_CATEGORIES
from src.logging_config import setup_logging

# === Configuración de página ===
st.set_page_config(
    page_title=f"{APP_NAME} — Asistente de Conocimiento Corporativo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Inicialización ===
setup_logging()


@st.cache_resource
def load_engine():
    """Carga el RAG Engine una sola vez."""
    return RAGEngine()


# === Sidebar ===
with st.sidebar:
    st.title(f"🧠 {APP_NAME}")
    st.caption("Asistente de Conocimiento Corporativo")

    st.divider()

    # Aviso obligatorio: es un agente de IA
    st.info(
        "⚠️ **Este es un agente de IA**. Las respuestas se generan automáticamente "
        "a partir de documentos internos. Verifica siempre la información con el "
        "área responsable antes de tomar decisiones críticas."
    )

    st.divider()

    # Filtro por categoría
    st.subheader("Filtrar por área")
    category_options = {"Todas las áreas": None}
    for key, val in BUSINESS_CATEGORIES.items():
        category_options[val["label"]] = key

    selected_category_label = st.selectbox(
        "Categoría de documentos:",
        options=list(category_options.keys()),
        index=0
    )
    category_filter = category_options[selected_category_label]

    st.divider()

    # Info de stack
    st.subheader("ℹ️ Stack")
    st.markdown("""
    - **LLM**: OCI Generative AI
    - **Embeddings**: BAAI/bge-m3 (local)
    - **Vector Store**: ChromaDB (HNSW)
    - **Framework**: LlamaIndex
    """)

    # Botón de limpiar historial
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()


# === Estado de sesión ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "engine" not in st.session_state:
    st.session_state.engine = load_engine()

# === Área principal de chat ===
st.title(f"🧠 {APP_NAME}")
st.markdown("*Pregunta lo que necesites sobre políticas, procesos y documentos internos de la empresa.*")
st.divider()

# Mostrar historial de mensajes
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Mostrar fuentes si es respuesta del asistente
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"📄 Fuentes consultadas ({len(msg['sources'])})"):
                for j, src in enumerate(msg["sources"], 1):
                    st.markdown(
                        f"**{j}. {src['file']}** "
                        f"(📂 {src['category']} | 📃 Pág. {src['page']} | "
                        f"🎯 Score: {src['score']})"
                    )
                    st.caption(src.get("preview", ""))
                    st.divider()

            # Mostrar confianza
            confidence = msg.get("confidence", 0)
            if confidence >= 0.7:
                st.success(f"Confianza: {confidence:.0%} ✅")
            elif confidence >= 0.4:
                st.warning(f"Confianza: {confidence:.0%} ⚠️")
            else:
                st.error(f"Confianza: {confidence:.0%} ❌")

            # Feedback buttons
            col1, col2, col3 = st.columns([1, 1, 8])
            feedback_key = f"feedback_{i}"
            with col1:
                if st.button("👍", key=f"up_{i}"):
                    st.session_state.feedback[feedback_key] = "positive"
                    save_feedback(msg, "positive")
                    st.toast("¡Gracias por tu feedback! 👍")
            with col2:
                if st.button("👎", key=f"down_{i}"):
                    st.session_state.feedback[feedback_key] = "negative"
                    save_feedback(msg, "negative")
                    st.toast("Gracias. Mejoraremos la respuesta. 👎")

            # Mostrar estado de feedback
            if feedback_key in st.session_state.feedback:
                fb = st.session_state.feedback[feedback_key]
                st.caption(f"Feedback registrado: {'👍 Positivo' if fb == 'positive' else '👎 Negativo'}")

# === Input del usuario ===
if prompt := st.chat_input("Escribe tu pregunta..."):
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Buscando en documentos internos..."):
            result = st.session_state.engine.ask(
                query=prompt,
                category_filter=category_filter
            )

        # Mostrar respuesta
        st.markdown(result["response"])

        # Mostrar fuentes
        if result["sources"]:
            with st.expander(f"📄 Fuentes consultadas ({len(result['sources'])})"):
                for j, src in enumerate(result["sources"], 1):
                    st.markdown(
                        f"**{j}. {src['file']}** "
                        f"(📂 {src['category']} | 📃 Pág. {src['page']} | "
                        f"🎯 Score: {src['score']})"
                    )
                    st.caption(src.get("preview", ""))
                    st.divider()

        # Confianza
        confidence = result.get("confidence", 0)
        if confidence >= 0.7:
            st.success(f"Confianza: {confidence:.0%} ✅")
        elif confidence >= 0.4:
            st.warning(f"Confianza: {confidence:.0%} ⚠️")
        else:
            st.error(f"Confianza: {confidence:.0%} ❌")

        # Latencia
        st.caption(f"⏱️ Respondido en {result['latency_ms']}ms")

    # Guardar en historial
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "sources": result["sources"],
        "confidence": result["confidence"],
        "latency_ms": result["latency_ms"]
    })


def save_feedback(msg: dict, feedback_type: str):
    """Persiste el feedback en un archivo JSONL para monitoreo."""
    feedback_path = Path("logs/feedback.jsonl")
    feedback_path.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": msg.get("content", "")[:200],
        "feedback": feedback_type,
        "confidence": msg.get("confidence", 0),
        "sources_count": len(msg.get("sources", []))
    }
    with open(feedback_path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

### 4.18 `scripts/ingest_documents.py` — Script CLI de ingestión

```python
#!/usr/bin/env python3
"""
YACHAY — Script de ingestión de documentos (CLI).
Uso: python scripts/ingest_documents.py
"""
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logging_config import setup_logging
from src.ingest.pipeline import run_ingestion_pipeline
from src.indexing.indexer import run_indexing_pipeline


def main():
    setup_logging()

    print("=" * 60)
    print("YACHAY — Ingestión e indexación de documentos")
    print("=" * 60)

    # 1. Ingestión (extraer + limpiar + chunk)
    chunks = run_ingestion_pipeline()

    if not chunks:
        print("❌ No se generaron chunks. Verifica los documentos en data/raw/")
        sys.exit(1)

    print(f"\n✅ Ingestión completa: {len(chunks)} chunks generados")

    # 2. Indexación (embeddings + Chroma)
    run_indexing_pipeline(chunks)

    print(f"\n✅ Indexación completa. El agente está listo para recibir preguntas.")
    print("Ejecuta: streamlit run app/app.py")


if __name__ == "__main__":
    main()
```

### 4.19 `scripts/test_query.py` — Script CLI para probar queries

```python
#!/usr/bin/env python3
"""
YACHAY — Script para probar queries desde la terminal (sin UI).
Uso: python scripts/test_query.py "¿Cuál es la política de vacaciones?"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logging_config import setup_logging
from src.rag_engine import RAGEngine


def main():
    setup_logging()

    if len(sys.argv) < 2:
        print("Uso: python scripts/test_query.py \"tu pregunta aquí\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"\n🔍 Pregunta: {query}\n")

    engine = RAGEngine()
    result = engine.ask(query)

    print(f"📝 Respuesta:\n{result['response']}\n")
    print(f"📄 Fuentes ({result['sources_count']}):")
    for s in result["sources"]:
        print(f"  - {s['file']} (cat: {s['category']}, pág: {s['page']}, score: {s['score']})")
    print(f"\n🎯 Confianza: {result['confidence']:.0%}")
    print(f"⏱️ Latencia: {result['latency_ms']}ms")
    print(f"⚠️ Fallback: {'Sí' if result['fallback_triggered'] else 'No'}")


if __name__ == "__main__":
    main()
```

### 4.20 `scripts/generate_sample_docs.py` — Generar documentos de ejemplo

```python
#!/usr/bin/env python3
"""
YACHAY — Genera documentos de ejemplo para poblar data/raw/.
Uso: python scripts/generate_sample_docs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATA_RAW_DIR


SAMPLE_DOCS = {
    "rrhh/politica-vacaciones.md": """# Política de Vacaciones — Empresa ACME Corp

## 1. Alcance
Esta política aplica a todos los colaboradores de ACME Corp con contrato vigente.

## 2. Días de vacaciones
- Colaboradores con menos de 1 año: 15 días calendario.
- Colaboradores con 1-5 años: 20 días calendario.
- Colaboradores con más de 5 años: 25 días calendario.

## 3. Procedimiento de solicitud
1. El colaborador debe solicitar vacaciones con mínimo 15 días de anticipación.
2. La solicitud se realiza vía el sistema de RRHH (portal interno).
3. El jefe directo debe aprobar la solicitud en un plazo de 3 días hábiles.
4. RRHH confirma la aprobación por correo electrónico.

## 4. Restricciones
- No se permiten vacaciones en períodos de cierre contable (última semana de cada trimestre).
- Máximo 2 colaboradores del mismo equipo en vacaciones simultáneamente.
- Las vacaciones no utilizadas pueden acumularse hasta 10 días al siguiente período.

## 5. Contacto
Área responsable: Gerencia de Recursos Humanos
Correo: rrhh@acmecorp.com
Teléfono: ext. 2100
""",

    "rrhh/beneficios-empleados.md": """# Beneficios para Colaboradores — ACME Corp

## 1. Seguro Médico
- Cobertura al 100% para el colaborador.
- Cobertura al 70% para dependientes directos (cónyuge e hijos menores de 25 años).
- Incluye consultas, hospitalización, medicamentos y atención de emergencia.

## 2. Bonificaciones
- Bono de productividad: hasta 2 sueldos adicionales al año, sujeto a evaluación de desempeño.
- Bono de antigüedad: 5% adicional por cada 5 años de servicio continuo.
- Bono navideño: 1 sueldo adicional en diciembre.

## 3. Capacitación
- Presupuesto anual de S/ 3,000 por colaborador para cursos y certificaciones.
- Convenios con universidades locales (UNSA, UCSM) con descuento del 30%.
- Licencia de estudio: hasta 5 días hábiles al año con goce de sueldo.

## 4. Otros beneficios
- Horario flexible (entrada entre 7:00-9:00, salida entre 16:00-18:00).
- Trabajo remoto: hasta 2 días por semana (previa coordinación con jefe directo).
- Comedor subsidiado: almuerzo a S/ 5.00 (subsidiado al 80%).

## 5. Contacto
Área responsable: Gerencia de Recursos Humanos
""",

    "financiero/politica-gastos.md": """# Política de Gastos y Reembolsos — ACME Corp

## 1. Principios generales
Todos los gastos deben ser estrictamente necesarios para la operación y contar con autorización previa del jefe directo.

## 2. Límites de gasto (sin aprobación adicional)
- Materiales de oficina: hasta S/ 200 por mes.
- Transporte (taxis/movilidad): hasta S/ 500 por mes.
- Representación (comidas con clientes): hasta S/ 300 por evento, máximo 2 eventos por mes.
- Viáticos nacionales: S/ 250 por día (incluye alojamiento, alimentación y transporte local).
- Viáticos internacionales: US$ 150 por día.

## 3. Proceso de reembolso
1. Presentar solicitud vía sistema financiero dentro de los 10 días calendario posteriores al gasto.
2. Adjuntar comprobante de pago válido (factura o boleta a nombre de ACME Corp, RUC 20123456789).
3. El jefe directo aprueba en un plazo de 5 días hábiles.
4. Finanzas procesa el reembolso en la siguiente nómina (15 o 30 de cada mes).

## 4. Gastos NO reembolsables
- Multas de tránsito.
- Bebidas alcohólicas.
- Gastos personales.
- Compras sin comprobante fiscal válido.

## 5. Contacto
Área responsable: Gerencia de Finanzas
Correo: finanzas@acmecorp.com
""",

    "legal/politica-privacidad.md": """# Política de Privacidad y Protección de Datos — ACME Corp

## 1. Marco legal
ACME Corp cumple con la Ley N° 29733 (Ley de Protección de Datos Personales del Perú) y su Reglamento (D.S. N° 003-2013-JUS).

## 2. Datos personales recopilados
- Datos de identificación: nombre, DNI, dirección, teléfono, correo.
- Datos laborales: cargo, área, fecha de ingreso, salario.
- Datos de salud: solo cuando sean estrictamente necesarios (seguro médico).

## 3. Finalidad del tratamiento
Los datos se recopilan exclusivamente para:
- Gestión de la relación laboral.
- Cumplimiento de obligaciones legales y tributarias.
- Administración de beneficios y seguros.

## 4. Derechos del titular
Todo colaborador puede ejercer sus derechos ARCO:
- **Acceso**: solicitar qué datos personales tenemos registrados.
- **Rectificación**: corregir datos inexactos.
- **Cancelación**: solicitar la eliminación de datos cuando ya no sean necesarios.
- **Oposición**: negarse al tratamiento de sus datos para finalidades no autorizadas.

## 5. Seguridad
- Datos almacenados en servidores con cifrado AES-256.
- Acceso restringido por roles (principio de mínimo privilegio).
- Auditorías de seguridad semestrales.

## 6. Contacto
Oficial de Protección de Datos: legal@acmecorp.com
""",

    "operacional/guia-incidentes.md": """# Guía de Gestión de Incidentes — ACME Corp

## 1. Definición de incidente
Un incidente es cualquier evento no planificado que interrumpe o reduce la calidad de un servicio de TI o proceso operativo.

## 2. Clasificación de severidad
- **P1 (Crítico)**: Servicio principal caído, afecta a más del 50% de usuarios. Tiempo de respuesta: 15 minutos. Tiempo de resolución: 4 horas.
- **P2 (Alto)**: Funcionalidad importante degradada, afecta a un área completa. Tiempo de respuesta: 30 minutos. Tiempo de resolución: 8 horas.
- **P3 (Medio)**: Funcionalidad secundaria afectada, workaround disponible. Tiempo de respuesta: 2 horas. Tiempo de resolución: 24 horas.
- **P4 (Bajo)**: Incidencia menor, impacto mínimo. Tiempo de respuesta: 8 horas. Tiempo de resolución: 72 horas.

## 3. Proceso de escalamiento
1. El usuario reporta el incidente vía mesa de ayuda (ext. 3000 o soporte@acmecorp.com).
2. Mesa de ayuda clasifica la severidad y asigna al equipo correspondiente.
3. Si no se resuelve en el tiempo estipulado, se escala al siguiente nivel:
   - Nivel 1: Soporte técnico → Nivel 2: Ingeniería → Nivel 3: Arquitectura / Gerencia de TI.
4. Para P1: se convoca automáticamente un "war room" con todos los niveles.

## 4. Post-mortem
Todo incidente P1 y P2 requiere un informe post-mortem dentro de las 48 horas, incluyendo:
- Cronología del incidente.
- Causa raíz.
- Acciones correctivas.
- Responsable de implementación.

## 5. Contacto
Área responsable: Gerencia de Operaciones / TI
Mesa de ayuda: ext. 3000
"""
}


def main():
    print("YACHAY — Generando documentos de ejemplo...\n")

    for rel_path, content in SAMPLE_DOCS.items():
        file_path = DATA_RAW_DIR / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        print(f"  ✅ {rel_path}")

    print(f"\n✅ {len(SAMPLE_DOCS)} documentos generados en {DATA_RAW_DIR}")
    print("Ahora ejecuta: python scripts/ingest_documents.py")


if __name__ == "__main__":
    main()
```

### 4.21 `docs/sources.md` — Mapeo de fuentes y ownership (Etapa 2)

```markdown
# YACHAY — Mapeo de Fuentes, Categorías y Ownership

## Fuentes de datos

| Fuente | Tipo | Acceso | Estado |
|---|---|---|---|
| Carpeta local `data/raw/` | Carga manual | Directo | ✅ Activo |
| OCI Object Storage | Bucket `yachay-docs` | API OCI SDK | ✅ Activo (deploy) |

## Categorías de negocio

| Categoría | Directorio | Responsable (Owner) | Descripción |
|---|---|---|---|
| **RRHH** | `data/raw/rrhh/` | Gerencia de Recursos Humanos | Políticas de personal, beneficios, onboarding, vacaciones |
| **Financiero** | `data/raw/financiero/` | Gerencia de Finanzas | Políticas de gastos, presupuestos, reembolsos |
| **Legal** | `data/raw/legal/` | Gerencia Legal | Privacidad, contratos, compliance, normativa |
| **Operacional** | `data/raw/operacional/` | Gerencia de Operaciones | Manuales de procesos, SLAs, gestión de incidentes |

## Curaduría de calidad

- **Duplicados**: se descartan automáticamente por hash de contenido durante la ingestión.
- **Versiones desactualizadas**: se mantiene solo la versión más reciente por nombre de archivo.
- **Revisión periódica**: cada owner revisa sus documentos trimestralmente.
- **Formatos soportados**: PDF, DOCX, XLSX, PPTX, MD, CSV, JSON, HTML, TXT.

## Proceso de ingesta

1. Colocar documentos en la subcarpeta correspondiente de `data/raw/`.
2. Ejecutar `python scripts/ingest_documents.py`.
3. El pipeline extrae, limpia, chunka e indexa automáticamente.
4. Para el deploy en OCI, los documentos se suben a Object Storage y se ingestan desde allí.
```

---

## 5. PLAN DE EJECUCIÓN DÍA POR DÍA

### DÍA 1 — Pipeline end-to-end funcional (lo que el evaluador revisa primero)

#### DÍA 1, Bloque 1 (mañana): Fundación + Ingestión

**Paso 1: Crear el repositorio** (~15 min)
```bash
# En GitHub: crear repo "yachay-rag-agent" (público, con README inicial)
git clone https://github.com/TU_USUARIO/yachay-rag-agent.git
cd yachay-rag-agent
```

**Paso 2: Crear estructura de directorios** (~10 min)
```bash
mkdir -p src/ingest src/indexing src/retrieval src/generation
mkdir -p app/components app/static
mkdir -p scripts tests docs/screenshots
mkdir -p data/raw/rrhh data/raw/financiero data/raw/legal data/raw/operacional
mkdir -p data/processed logs chroma_db oci

# Crear archivos __init__.py
touch src/__init__.py src/ingest/__init__.py src/indexing/__init__.py
touch src/retrieval/__init__.py src/generation/__init__.py
touch tests/__init__.py

# Crear .gitkeep para directorios vacíos
touch data/processed/.gitkeep logs/.gitkeep chroma_db/.gitkeep
```

**Paso 3: Crear archivos de configuración** (~15 min)
```bash
# Copiar los contenidos de la sección 3 de esta guía:
# - .gitignore
# - .env.example
# - requirements.txt
# - Makefile
```

**Paso 4: Setup del entorno local** (~10 min)

En Windows, si tienes varias versiones de Python instaladas (3.12, 3.14, etc.), usa el `py launcher` para forzar 3.11.9 y no interferir con las otras:

```bash
# Verificar qué versiones tienes:
py --list

# Crear el venv forzando 3.11 (Windows):
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac:
# python3.11 -m venv venv
# source venv/bin/activate

# Si vas a usar tu GPU (RTX 4050) para acelerar los embeddings, instala PyTorch con CUDA ANTES del resto:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu API Key real de OCI GenAI

# Verificar GPU (opcional):
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

**Paso 5: Documentos fuente para la ingestión** (~5 min)

Ya no hace falta generar documentos sintéticos: tienes **16 documentos reales de la empresa ficticia NovaTech Perú S.A.C.**, listos para colocar en `data/raw/` con la clasificación exacta que espera el pipeline:

```
data/raw/
├── rrhh/            (5 docs: vacaciones, manual del colaborador, beneficios, trabajo remoto, onboarding)
├── financiero/      (4 docs: gastos y reembolsos, caja chica, compras, facturación y cobranzas)
├── legal/           (3 docs: privacidad de datos, ética y anticorrupción, reglamento interno)
└── operacional/     (4 docs: gestión de incidentes, continuidad de negocio, seguridad de la información, SLA proveedores)
```

Descarga los 16 archivos `.md` que ya se generaron en esta conversación y colócalos en las subcarpetas correspondientes según el nombre indicado arriba. Si prefieres tener también documentos de ejemplo genéricos adicionales, `scripts/generate_sample_docs.py` sigue disponible como complemento opcional:
```bash
python scripts/generate_sample_docs.py
# Verifica: ls data/raw/rrhh/ data/raw/financiero/ data/raw/legal/ data/raw/operacional/
```

**Paso 6: Crear los módulos de ingestión** (~60 min)
```bash
# Crear estos archivos con el código de la sección 4:
# - src/config.py
# - src/logging_config.py
# - src/ingest/extractors.py
# - src/ingest/chunker.py
# - src/ingest/cleaner.py
# - src/ingest/pipeline.py
# - scripts/ingest_documents.py
```

**Paso 7: Ejecutar ingestión** (~5 min)
```bash
python scripts/ingest_documents.py
# Verificar: cat data/catalog.json | python -m json.tool | head -30
# Verificar: ls data/processed/chunks.json
```

**CHECKPOINT 1**: Tienes chunks procesados con metadatos. ✅

#### DÍA 1, Bloque 2 (mediodía): Indexación + Retrieval

**Paso 8: Crear módulos de indexación** (~30 min)
```bash
# Crear:
# - src/indexing/embedder.py
# - src/indexing/vector_store.py
# - src/indexing/indexer.py
```

**Paso 9: Ejecutar indexación** (~15-30 min dependiendo de la máquina)
```bash
python scripts/ingest_documents.py  # Re-ejecuta ingestión + indexación
# La primera vez descarga bge-m3 (~2GB). Luego genera embeddings.
```

**Paso 10: Crear módulos de retrieval** (~30 min)
```bash
# Crear:
# - src/retrieval/retriever.py
# - src/retrieval/reranker.py
# - src/retrieval/context_builder.py
```

**CHECKPOINT 2**: Puedes buscar chunks por similitud semántica desde CLI. ✅

#### DÍA 1, Bloque 3 (tarde): LLM + UI + Pipeline completo

**Paso 11: Crear módulos de generación** (~30 min)
```bash
# Crear:
# - src/generation/llm_client.py
# - src/generation/prompts.py
# - src/generation/response_validator.py
```

**Paso 12: Crear el orquestador RAG** (~15 min)
```bash
# Crear: src/rag_engine.py
```

**Paso 13: Probar el pipeline completo en CLI** (~10 min)
```bash
# Crear: scripts/test_query.py
python scripts/test_query.py "¿Cuántos días de vacaciones tengo si llevo 3 años?"
python scripts/test_query.py "¿Cuál es el límite de gastos de transporte?"
python scripts/test_query.py "¿Cómo reporto un incidente P1?"
python scripts/test_query.py "¿Cuál es la receta del ceviche?" # Debe dar fallback
```

**CHECKPOINT 3**: El pipeline responde preguntas con fuentes citadas desde terminal. ✅

**Paso 14: Crear la interfaz Streamlit** (~60 min)
```bash
# Crear: app/app.py
streamlit run app/app.py
# Abrir http://localhost:8501 y probar
```

**Paso 15: Commit del Día 1** (~10 min)
```bash
git add .
git commit -m "feat: pipeline RAG completo — ingestión, indexación, retrieval, generación, UI Streamlit"
git push origin main
```

**CHECKPOINT 4 (fin del Día 1)**: App funcional localmente con chat, fuentes, feedback e historial. ✅

---

### DÍA 2 — Deploy en OCI + Evidencia + README

#### DÍA 2, Bloque 1 (mañana): Docker + OCI

**Paso 16: Dockerizar** (~30 min)
```bash
# Crear: Dockerfile (sección 3.4)
# Crear: .dockerignore
echo "venv/\n.env\n__pycache__/\n.git/\nchroma_db/\nlogs/" > .dockerignore

docker build -t yachay-rag-agent:latest .
docker run -d --name yachay -p 8501:8501 --env-file .env \
  -v $(pwd)/data/raw:/app/data/raw:ro \
  yachay-rag-agent:latest

# Verificar: abrir http://localhost:8501
docker logs yachay
```

**Paso 17: Configurar servicios OCI** (~90 min)

```bash
# A) OCI Object Storage — subir documentos
# Consola OCI → Storage → Object Storage → Create Bucket: "yachay-docs"
# Subir los archivos de data/raw/ al bucket

# B) OCI Vault — guardar API Key
# Consola OCI → Identity & Security → Vault → Create Vault: "yachay-vault"
# Create Secret: nombre="oci-genai-api-key", contenido=tu API key

# C) OCI Container Registry — subir imagen Docker
# Consola OCI → Developer Services → Container Registry
# Crear repositorio: "yachay-rag-agent"

# Tag y push de la imagen:
export OCI_REGION=sa-saopaulo-1
export OCI_TENANCY_NAMESPACE=tu_namespace  # ver en: Consola → Tenancy Information
export OCIR_URL=${OCI_REGION}.ocir.io/${OCI_TENANCY_NAMESPACE}/yachay-rag-agent

docker tag yachay-rag-agent:latest ${OCIR_URL}:latest
docker login ${OCI_REGION}.ocir.io -u "${OCI_TENANCY_NAMESPACE}/tu_email" -p "tu_auth_token"
docker push ${OCIR_URL}:latest

# D) OCI Compute — crear instancia
# Consola OCI → Compute → Instances → Create Instance
# - Shape: VM.Standard.A1.Flex (2 OCPU, 12 GB RAM — Always Free)
# - Image: Oracle Linux 8 o Ubuntu 22.04
# - VCN: crear una nueva con subnet pública
# - SSH key: tu clave pública
# - Abrir puerto 8501 en Security List del subnet

# E) SSH a la instancia y configurar
ssh -i tu_key.pem opc@IP_PUBLICA

# En la VM:
sudo yum install -y docker    # Oracle Linux
# o: sudo apt install -y docker.io   # Ubuntu
sudo systemctl start docker
sudo usermod -aG docker $USER
# Re-login para aplicar grupo docker

# Login a OCIR y descargar imagen
docker login ${OCI_REGION}.ocir.io
docker pull ${OCIR_URL}:latest

# Crear .env en la VM con la API Key (o inyectar desde Vault)
cat > .env << 'EOF'
OCI_GENAI_API_KEY=tu_api_key_real
OCI_REGION=sa-saopaulo-1
OCI_CHAT_MODEL=meta.llama-3.3-70b-instruct
OCI_GENAI_BASE_URL=https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com/openai/v1
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024
CHROMA_PERSIST_DIR=/app/chroma_db
CHROMA_COLLECTION_NAME=yachay_docs
EOF

# Ejecutar la app
docker run -d --name yachay -p 8501:8501 --env-file .env \
  ${OCIR_URL}:latest

# La primera ejecución descargará bge-m3 e indexará los docs dentro del contenedor
# Verificar: curl http://localhost:8501
```

**CHECKPOINT 5**: App corriendo en OCI Compute accesible por IP pública. ✅

#### DÍA 2, Bloque 2 (mediodía): Logging + Evidencia

**Paso 18: Configurar OCI Logging** (~30 min)
```bash
# Consola OCI → Observability & Management → Logging → Log Groups
# Crear Log Group: "yachay-logs"
# Crear Custom Log: "yachay-rag-interactions"
# (Los logs de Docker se capturan automáticamente; para envío custom,
#  usar el OCI Logging Ingestion API o un fluentd agent)

# Alternativa rápida: simplemente mostrar docker logs como evidencia
docker logs yachay 2>&1 | grep "RAG_INTERACTION" > evidencia_logs.txt
```

**Paso 19: Capturar evidencia multimedia** (~30 min)
```bash
# OBLIGATORIO: foto o video de la app funcionando EN LA NUBE

# Opción 1: Captura de pantalla
# - Navegar a http://IP_PUBLICA:8501
# - Hacer varias preguntas
# - Capturar pantallazos de:
#   1. La app respondiendo con fuentes citadas
#   2. El sidebar indicando "Este es un agente de IA"
#   3. Los botones de feedback
#   4. La consola OCI mostrando la instancia running
#   5. Object Storage con los documentos
#   6. Los logs de trazabilidad (pregunta → documento → respuesta)

# Opción 2: Video corto (30-60 seg)
# - Grabar la pantalla navegando la app en la IP pública de OCI
# - Mostrar: pregunta → respuesta citada → fuentes → feedback → logs

# Guardar en docs/screenshots/
```

**CHECKPOINT 6**: Evidencia multimedia capturada. ✅

#### DÍA 2, Bloque 3 (tarde): README + Pulido final

**Paso 20: Escribir el README final** (~90 min)
```bash
# Usar el esqueleto de la sección F del reporte de arquitectura
# Incluir:
# 1. Resumen ejecutivo con datos de McKinsey/Gartner
# 2. Demo: GIF o video embebido
# 3. Diagrama mermaid de arquitectura
# 4. Tabla de stack técnico
# 5. Instrucciones de instalación local
# 6. Pasos de deploy en OCI
# 7. Capturas de evidencia en nube
# 8. Decisiones de diseño y trade-offs
# 9. Limitaciones y trabajo futuro
# 10. Checklist de las 10 etapas cubiertas
```

**Paso 21: Crear docs/trade-offs.md** (~30 min)
```markdown
# Documenta estas decisiones clave:
1. Por qué meta.llama-3.3-70b-instruct y no Cohere Command A
   → Endpoint OpenAI-compatible no soporta modelos Cohere
2. Por qué embeddings locales (bge-m3) y no OCI Embed 4
   → Embed 4 on-demand no está en São Paulo; endpoint incompatible
3. Por qué Chroma y no Oracle 23ai AI Vector Search
   → Velocidad de setup para 2 días; HNSW nativo
4. Por qué Streamlit y no Next.js/React
   → Time-to-MVP; cumple todos los requisitos de UI
5. Por qué no OKE (Kubernetes)
   → Overengineering para este scope; Compute/Container Instances suficiente
```

**Paso 22: Commits finales y limpieza** (~15 min)
```bash
git add .
git commit -m "feat: deploy OCI + evidencia + README final"
git push origin main

# Verificar que el README se vea bien en GitHub
# Verificar que las imágenes en docs/screenshots/ se muestren
# Verificar que .env NO esté en el repo (debe estar en .gitignore)
```

**CHECKPOINT 7 (ENTREGA)**: Repositorio completo con todas las etapas cubiertas. ✅

---

## 6. CHECKLIST FINAL DE ENTREGA

| # | Etapa | Requisito | Estado |
|---|---|---|---|
| 1 | Repositorio GitHub | Repo con README que documenta funcionalidades + capturas/video | ☐ |
| 2 | Colecta de documentos | Mapeo de fuentes, categorías, ownership, curaduría, ingesta | ☐ |
| 3 | Procesamiento | Extracción multi-formato, OCR, limpieza, chunking, metadatos | ☐ |
| 4 | Indexación vectorial | Embeddings (bge-m3), Chroma con HNSW, metadatos indexados | ☐ |
| 5 | Recuperación RAG | Query→embedding, similitud coseno, filtro metadatos, rerank, contexto | ☐ |
| 6 | Respuestas validadas | Solo contexto, citación exacta, anti-alucinación, fallback | ☐ |
| 7 | Interfaz | Chat web (Streamlit), "es IA", fuentes, feedback 👍/👎, historial | ☐ |
| 8 | Deploy OCI | ≥1 servicio OCI (Object Storage + Compute + Vault + Logging) | ☐ |
| 9 | Registro de ejecución | Evidencia foto/video, trazabilidad pregunta→doc→respuesta, logs | ☐ |
| 10 | README final | Descripción, arquitectura, stack, setup, deploy, decisiones, limitaciones | ☐ |
| — | API Key segura | En Vault/env, creada en la misma región, NUNCA hardcodeada | ☐ |
| — | Solo Chat API | NO GenerateText/SummarizeText (deprecados 26-jun-2026) | ☐ |

---

## 7. COMANDOS DE REFERENCIA RÁPIDA

```bash
# === Desarrollo local ===
make setup                   # Crear venv + instalar deps
make generate-docs           # Generar documentos de ejemplo
make ingest                  # Ingestión e indexación completa
make run                     # Lanzar Streamlit (localhost:8501)
make query Q="mi pregunta"   # Probar query desde terminal

# === Docker ===
make docker-build            # Construir imagen
make docker-run              # Ejecutar contenedor
docker logs yachay -f        # Ver logs en tiempo real

# === OCI ===
docker push ${OCIR_URL}:latest      # Subir imagen a OCIR
ssh -i key.pem opc@IP_PUBLICA       # Conectar a la VM
docker logs yachay 2>&1 | grep RAG   # Extraer logs de interacciones
```

---

*Generado como guía de ejecución para el proyecto YACHAY — Agente RAG Corporativo sobre OCI Generative AI.*
*Stack: Python 3.11.9 | OCI GenAI (Llama 3.3 70B) | bge-m3 | Chroma | LlamaIndex | Streamlit*
*Última actualización: corregida versión de Python (3.11.9, no 3.11.12) y referencia a los 16 documentos reales de NovaTech Perú S.A.C. ya generados para la ingestión.*
