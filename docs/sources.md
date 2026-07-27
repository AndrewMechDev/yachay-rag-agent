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

**Deploy (Fase 6)**: aún no definido. La sección "Para el deploy en OCI" más
abajo queda obsoleta hasta decidir el reemplazo (candidatos: Render, Fly.io,
Railway, o un VPS con Docker Compose).

## Fuentes de datos

| Fuente | Tipo | Acceso | Estado |
|---|---|---|---|
| Carpeta local `data/raw/` | Carga manual (16 documentos `.md`) | Directo | ✅ Activo |
| Object Storage en la nube | Bucket para deploy | Por definir | ⏳ Pendiente (ver decisión de deploy arriba) |

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
   embeddings con `bge-m3` → indexa en ChromaDB, en un solo paso.
4. Se generan dos artefactos:
   - `data/catalog.json` — catálogo de documentos con categoría/owner (versionado en git).
   - `data/processed/chunks.json` — chunks listos para indexar (ignorado en git).
5. Para el deploy en OCI (Fase 6, pendiente): los documentos se subirán a
   Object Storage y se ingestarán desde allí en vez de `data/raw/` local.
