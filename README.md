---
title: YACHAY
emoji: 🧠
colorFrom: yellow
colorTo: indigo
sdk: docker
app_port: 8501
pinned: false
---

# YACHAY

> **YACHAY** (quechua: *conocimiento, saber*) — Agente RAG corporativo que responde preguntas de colaboradores a partir de documentos internos.

## Qué es

YACHAY busca en documentos internos (políticas, manuales, procedimientos), recupera los fragmentos relevantes y genera una respuesta citando la fuente exacta. Si no encuentra información suficiente, lo dice explícitamente en vez de inventar.

## Stack

- Python 3.11.9
- LlamaIndex + ChromaDB (vector store local)
- Embeddings: `BAAI/bge-m3` (local, GPU CUDA)
- LLM: Groq (`llama-3.3-70b-versatile`) vía endpoint compatible con OpenAI — se descartó OCI Generative AI por bloqueos del antifraude en el registro de cuenta gratuita de Oracle (ver `docs/sources.md`)
- UI: Streamlit
- Deploy: por definir (pendiente, ver `docs/sources.md`)

## Setup local

```bash
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
copy .env.example .env
# Editar .env con tu API Key de Groq (opcional, ver más abajo) — gratis en https://console.groq.com/keys
```

## Uso

```bash
python scripts/ingest_documents.py
python scripts/test_query.py "¿Cuántos días de vacaciones tengo si llevo 3 años?"
python run_app.py
```

> **Windows**: usa `python run_app.py`, **no** `streamlit run app/app.py` directamente.
> Este entrypoint pre-carga el RAG Engine (torch + chromadb) en el hilo principal
> antes de arrancar Streamlit. Es necesario porque, en Windows, torch y chromadb
> juntos crashean el proceso (`STATUS_ACCESS_VIOLATION 0xC0000005` en `WINHTTP.dll`)
> si se inicializan desde el hilo secundario donde Streamlit ejecuta el script
> ("ScriptRunner"). Ver `src/engine_singleton.py` para el diagnóstico completo.
> En Linux/macOS ambas formas funcionan igual.

## Cómo probarlo ya mismo (sin API key de LLM)

El pipeline de ingestión, indexación y retrieval **no depende de ningún LLM**:
solo la generación de la respuesta final lo necesita. Mientras no tengas
`LLM_API_KEY` configurada (o el placeholder de `.env.example` siga tal cual),
el sistema usa automáticamente un `MockLLMClient` que **no inventa texto**: te
devuelve exactamente los fragmentos recuperados con su fuente y score, para
que puedas validar que el retrieval funciona.

1. Verifica que ya corriste la ingestión al menos una vez (genera `chroma_db/`):
   ```bash
   python scripts/ingest_documents.py
   ```
2. Prueba una pregunta desde la terminal, sin interfaz:
   ```bash
   python scripts/test_query.py "¿Cuál es el límite de gastos de transporte?"
   ```
   Vas a ver en la respuesta el prefijo `[MODO MOCK — sin conexión al LLM...]`
   seguido del contexto real recuperado (archivo, sección, score). Eso confirma
   que el buscador semántico está funcionando correctamente sobre tus 16
   documentos.
3. Pruébalo con interfaz de chat completa:
   ```bash
   python run_app.py
   ```
   Se abre en `http://localhost:8501`. Ahí puedes chatear, filtrar por categoría
   (RRHH/Financiero/Legal/Operacional), ver las fuentes citadas por respuesta y
   dar feedback 👍/👎.
4. **Cuando tengas tu API Key de Groq** (gratis, sin tarjeta, en
   [console.groq.com/keys](https://console.groq.com/keys)): solo edítala en
   `.env` (`LLM_API_KEY=...`). No hay que tocar código ni reiniciar nada más
   que el proceso — `get_llm_client()` detecta la key real y cambia
   automáticamente de `MockLLMClient` a `RemoteLLMClient`.

Preguntas de ejemplo para probar (ya validadas contra los documentos reales):
- "¿Cuántos días de vacaciones tengo si llevo 3 años?"
- "¿Cuál es el límite de gastos de transporte?"
- "¿Cómo reporto un incidente P1?"
- "¿Cuál es la receta del ceviche?" (pregunta fuera de dominio, para ver cómo reacciona el sistema)

## Deploy (Hugging Face Spaces)

Se descartó OCI Compute/Object Storage junto con OCI GenAI (ver `docs/sources.md`).
El deploy usa **Hugging Face Spaces** (SDK Docker): gratis, sin tarjeta, con
16GB RAM / 2 vCPU en el tier CPU básico — de sobra para `bge-m3` + ChromaDB +
Streamlit, y pensado justo para este tipo de demo. `data/raw/` (16 `.md`) está
versionado en git, así que la ingestión/indexación corre dentro del propio
`Dockerfile` en build time; no hay disco persistente ni Object Storage.

1. Crea cuenta en [huggingface.co](https://huggingface.co) y un token con
   permiso de escritura en [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Crea el Space en [huggingface.co/new-space](https://huggingface.co/new-space):
   SDK **Docker**, hardware **CPU basic** (free), visibilidad a tu gusto.
3. En el Space → **Settings → Variables and secrets**, agrega como *secret*:
   `LLM_API_KEY` con tu API Key de Groq. (Opcional: `LLM_CHAT_MODEL` /
   `LLM_BASE_URL` si algún día cambias de proveedor sin tocar código).
4. Conecta el repo local al Space y sube el código:
   ```bash
   git remote add space https://huggingface.co/spaces/<tu-usuario>/<nombre-space>
   git push space main
   ```
   (te pedirá login: usuario = tu usuario de HF, password = el token del paso 1).
5. HF construye la imagen automáticamente (tarda varios minutos por el modelo
   `bge-m3` + la ingestión). Revisa el progreso en la pestaña **Logs** del Space.
6. Cuando el estado pase a **Running**, la app queda pública en
   `https://huggingface.co/spaces/<tu-usuario>/<nombre-space>`.

Si subes documentos nuevos a `data/raw/`, hay que volver a hacer
`git push space main` para que se reconstruya la imagen con la ingestión
actualizada (no hay hot-reload de datos en este esquema).

## Estructura

Ver `yachay-execution-guide.md` sección 2 para el detalle completo del repositorio.
Mapeo de fuentes, categorías y ownership de documentos: `docs/sources.md`.

## Documentos fuente

16 documentos `.md` en `data/raw/` organizados en `rrhh/`, `financiero/`, `legal/`, `operacional/`, sobre una empresa ficticia (NovaTech Perú S.A.C.) con contexto peruano real (Ley 29733, D.S. 003-97-TR, EsSalud, etc.).
