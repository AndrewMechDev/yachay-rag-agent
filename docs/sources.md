# YACHAY — Mapeo de Fuentes, Categorías y Ownership

## Decisión: se descartó OCI (LLM y, probablemente, deploy)

El plan original usaba OCI Generative AI para la generación y OCI Compute /
Object Storage para el deploy. Se descartó el LLM de OCI porque el registro
de cuenta gratuita de Oracle quedó bloqueado repetidamente por su sistema
antifraude ("se ha producido un error al crear su cuenta", con tarjeta válida
y datos correctos verificados con el banco) — un problema ampliamente
reportado y no atribuible a un error del usuario.

**Reemplazo de LLM**: [Groq](https://console.groq.com) (`llama-3.3-70b-versatile`),
vía su endpoint compatible con OpenAI. Registro gratis sin tarjeta, sin
verificación antifraude. El cambio no tocó `rag_engine.py` ni el resto del
pipeline — solo `src/generation/llm_client.py` (renombrado `OCIGenAIClient` →
`RemoteLLMClient`) y las variables de entorno (`OCI_GENAI_*` → `LLM_*`),
gracias a que ya estaba detrás de una interfaz (`yachay-buenas-practicas`).

**Deploy (Fase 6) — segundo cambio de plan**: se probó primero Hugging Face
Spaces (SDK Docker, 16GB RAM / 2 vCPU gratis). Funcionó hasta que, en julio
2026, HF empezó a exigir suscripción **PRO** de pago para crear Spaces con
Docker o Gradio — cambio de política sin aviso ni actualización de su página
de precios (reportado por varios usuarios en discuss.huggingface.co el mismo
mes). Solo quedaron gratis los Spaces "Static" (HTML/JS puro, sin backend
Python, no sirve para esta app).

**Reemplazo de deploy**: [Streamlit Community Cloud](https://share.streamlit.io),
el hosting oficial del propio framework Streamlit. Gratis, sin tarjeta nunca,
deploy directo desde GitHub sin necesidad de Dockerfile. Su límite de RAM
(~1-2.7GB) es más ajustado que el de HF Spaces, así que se cambió el modelo de
embeddings de `BAAI/bge-m3` (2.2GB) a `paraphrase-multilingual-MiniLM-L12-v2`
(~470MB) — ver `src/config.py`. Como esta plataforma no tiene un paso de build
propio ni disco persistente garantizado, `src/engine_singleton.py` corre la
ingestión + indexación automáticamente si detecta el vector store vacío al
arrancar. Ver instrucciones paso a paso en el `README.md`.

## Fuentes de datos

| Fuente | Tipo | Acceso | Estado |
|---|---|---|---|
| Carpeta local `data/raw/` | Carga manual (16 documentos `.md`) | Directo | ✅ Activo |
| Object Storage en la nube | Bucket para deploy | Descartado — sin disco persistente en Streamlit Community Cloud, se re-ingesta desde `data/raw/` (versionado en git) en cada arranque en frío | ❌ Descartado |

## Categorías de negocio

| Categoría | Directorio | Responsable (Owner) | Descripción |
|---|---|---|---|
| **RRHH** | `data/raw/rrhh/` | Gerencia de Recursos Humanos | Políticas de personal, beneficios, onboarding, vacaciones |
| **Financiero** | `data/raw/financiero/` | Gerencia de Finanzas | Políticas de gastos, presupuestos, reembolsos, compras |
| **Legal** | `data/raw/legal/` | Gerencia Legal | Privacidad, contratos, compliance, normativa |
| **Operacional** | `data/raw/operacional/` | Gerencia de Operaciones | Manuales de procesos, SLAs, gestión de incidentes |

La categoría se detecta automáticamente por la carpeta padre del documento
(`src/ingest/pipeline.py::detect_category`), definida en `BUSINESS_CATEGORIES`
(`src/config.py`).

## Estado actual de la curaduría (honesto, no aspiracional)

- **Segmentación**: cada documento `.md` se divide por encabezado (`##`), no por
  archivo completo — permite citar la sección exacta de origen.
- **Deduplicación por hash**: **no implementada todavía**. Si se sube el mismo
  documento dos veces, generará chunks duplicados en el índice. Pendiente para
  una iteración futura si el volumen de documentos crece.
- **Versionado**: no hay control de versiones de documentos; se asume que
  `data/raw/` siempre refleja la versión vigente. Re-ejecutar la ingestión
  reemplaza el catálogo pero no limpia el vector store (ver nota abajo).
- **Formatos soportados por el extractor**: `.pdf .docx .xlsx .pptx .md .csv .json .html .txt`
  (`src/ingest/extractors.py`), aunque hoy solo se usan los 16 `.md` reales.

> **Nota operativa**: si vas a re-ingestar tras cambiar chunking/extracción,
> borra `chroma_db/` antes de correr `python scripts/ingest_documents.py` para
> evitar que queden chunks viejos junto a los nuevos (no hay `reset()`
> automático en el pipeline; `ChromaVectorStore.reset()` existe pero debe
> invocarse manualmente).

## Proceso de ingesta

1. Colocar documentos en la subcarpeta correspondiente de `data/raw/<categoria>/`.
2. Ejecutar `python scripts/ingest_documents.py`.
3. El pipeline extrae → limpia → chunkea (512 palabras, overlap 80) → genera
   embeddings (`paraphrase-multilingual-MiniLM-L12-v2`, ver `src/config.py`) →
   indexa en ChromaDB, en un solo paso.
4. Se generan dos artefactos:
   - `data/catalog.json` — catálogo de documentos con categoría/owner (versionado en git).
   - `data/processed/chunks.json` — chunks listos para indexar (ignorado en git).
5. En Streamlit Community Cloud (Fase 6, deploy actual) este pipeline corre
   automáticamente al arrancar si el vector store está vacío (ver
   `src/engine_singleton.py`); no hay Object Storage ni disco persistente, así
   que `data/raw/` (versionado en git) es la única fuente de verdad.
