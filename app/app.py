"""Interfaz de chat con Streamlit. Sistema visual glassmorphism (ver skill
yachay-ui-streamlit). Indica que es un agente de IA, muestra fuentes citadas,
permite feedback e historial por sesión."""

import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Debe fijarse antes de importar src.rag_engine (que importa el embedder):
# el server real de Streamlit crashea de forma intermitente al usar CUDA
# junto a su ScriptRunner en Windows (ver yachay-buenas-practicas / commit
# de este fix). Forzamos CPU solo para la app en vivo; la ingestión por CLI
# sigue usando GPU.
os.environ["YACHAY_FORCE_CPU_EMBEDDER"] = "1"

from src.config import APP_NAME, BUSINESS_CATEGORIES
from src.logging_config import setup_logging
from src.rag_engine import RAGEngine

st.set_page_config(
    page_title=f"{APP_NAME} — Asistente de Conocimiento Corporativo",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()

STATIC_DIR = Path(__file__).resolve().parent / "static"
_avatar_assistant_path = STATIC_DIR / "avatar-assistant.png"
_avatar_user_path = STATIC_DIR / "avatar-user.png"
# Fallback a emoji si aún no se agregaron los PNG reales en app/static/
# (evita que st.chat_message falle buscando un archivo inexistente).
AVATAR_ASSISTANT = str(_avatar_assistant_path) if _avatar_assistant_path.exists() else "🧠"
AVATAR_USER = str(_avatar_user_path) if _avatar_user_path.exists() else "🙂"

THEME_CSS = """
<style>
:root {
    --yachay-bg-1: #1b2140;
    --yachay-bg-2: #0B0F1A;
    --yachay-bg-3: #05070c;
    --yachay-accent: #D4A855;
    --yachay-text: #EDEBFF;
    --yachay-font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    --yachay-glass-bg: rgba(255, 255, 255, 0.035);
    --yachay-glass-border: rgba(255, 255, 255, 0.10);
    --yachay-radius: 20px;
}

html, body, .stApp, [class*="css"] {
    font-family: var(--yachay-font) !important;
}

.stApp {
    background: radial-gradient(circle at top left, var(--yachay-bg-1) 0%, var(--yachay-bg-2) 55%, var(--yachay-bg-3) 100%);
}

@keyframes yachay-fade-in {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--yachay-glass-border);
}

[data-testid="stChatMessage"] {
    background: var(--yachay-glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: var(--yachay-radius);
    padding: 1rem 1rem;
    margin-bottom: 0.5rem;
    animation: yachay-fade-in 0.25s ease-out;
}

[data-testid="stExpander"] {
    background: var(--yachay-glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 16px;
}

[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(212, 168, 85, 0.3);
    border-radius: 16px;
}

div.stButton > button {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(8px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 12px;
    color: var(--yachay-text);
    transition: border-color 0.2s ease-out, color 0.2s ease-out, transform 0.1s ease-out;
}
div.stButton > button:hover {
    border-color: var(--yachay-accent);
    color: var(--yachay-accent);
}
div.stButton > button:active {
    transform: scale(0.97);
}

.brand-title {
    font-size: 2.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, var(--yachay-accent), var(--yachay-text));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.brand-title.sidebar {
    font-size: 1.5rem;
}
.brand-subtitle {
    color: rgba(237, 235, 255, 0.7);
    font-size: 1rem;
    margin-top: 0.25rem;
}
.caption-text {
    color: rgba(237, 235, 255, 0.65);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.glass-card {
    background: var(--yachay-glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--yachay-glass-border);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    animation: yachay-fade-in 0.2s ease-out;
}

.glass-alert {
    background: rgba(212, 168, 85, 0.07);
    backdrop-filter: blur(12px);
    border-left: 3px solid var(--yachay-accent);
    border-radius: 12px;
    padding: 1rem;
    font-size: 0.875rem;
    color: var(--yachay-text);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8125rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
    border: 1px solid var(--yachay-glass-border);
}
.badge-high { background: rgba(94, 219, 138, 0.15); color: #6EE7A8; border-color: rgba(94, 219, 138, 0.4); }
.badge-medium { background: rgba(212, 168, 85, 0.15); color: var(--yachay-accent); border-color: rgba(212, 168, 85, 0.4); }
.badge-low { background: rgba(224, 92, 92, 0.15); color: #F08787; border-color: rgba(224, 92, 92, 0.4); }

.source-title { font-weight: 600; color: var(--yachay-text); }
.source-meta { color: rgba(237, 235, 255, 0.68); font-size: 0.8125rem; }

.badge-mock {
    background: rgba(224, 92, 92, 0.12);
    color: #F0A787;
    border-color: rgba(224, 92, 92, 0.35);
}
.badge-live {
    background: rgba(94, 219, 138, 0.12);
    color: #6EE7A8;
    border-color: rgba(94, 219, 138, 0.35);
}

@keyframes yachay-skeleton-pulse {
    0%, 100% { opacity: 0.35; }
    50% { opacity: 0.7; }
}
.skeleton-line {
    height: 0.9rem;
    border-radius: 6px;
    background: var(--yachay-glass-border);
    animation: yachay-skeleton-pulse 1.1s ease-in-out infinite;
    margin-bottom: 0.6rem;
}

h1, h2, h3 { color: var(--yachay-text) !important; font-weight: 600 !important; }

@media (prefers-reduced-motion: reduce) {
    [data-testid="stChatMessage"], .glass-card {
        animation: none !important;
    }
    div.stButton > button {
        transition: none !important;
    }
    .skeleton-line {
        animation: none !important;
        opacity: 0.5 !important;
    }
}

@media (max-width: 480px) {
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        min-width: 100% !important;
    }
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


def save_feedback(msg: dict, feedback_type: str) -> None:
    """Persiste el feedback en logs/feedback.jsonl para monitoreo."""
    feedback_path = Path("logs/feedback.jsonl")
    feedback_path.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": msg.get("query", "")[:200],
        "feedback": feedback_type,
        "confidence": msg.get("confidence", 0),
        "sources_count": len(msg.get("sources", [])),
    }
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def render_sources(sources: list) -> None:
    """Renderiza el expander de fuentes citadas como glass cards, con la cita
    en un st.code para que el usuario pueda copiarla (ícono nativo de Streamlit)."""
    with st.expander(f"Fuentes consultadas ({len(sources)})"):
        for j, src in enumerate(sources, 1):
            st.markdown(
                f"""<div class="glass-card">
                    <div class="source-title">{j}. {src['file']}</div>
                    <div class="source-meta">Categoría: {src['category']} · Sección: {src['section']} · Score: {src['score']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            citation = f"{src['file']} · {src['section']}\n\n{src.get('preview', '')}"
            st.code(citation, language=None)


def render_skeleton() -> str:
    """Devuelve el markup de un placeholder tipo 'skeleton' mientras se busca la respuesta."""
    return (
        '<div class="skeleton-line" style="width: 90%;"></div>'
        '<div class="skeleton-line" style="width: 75%;"></div>'
        '<div class="skeleton-line" style="width: 50%;"></div>'
    )


def stream_response(text: str, chunk_words: int = 6, delay: float = 0.02):
    """Generador para el efecto typewriter: solo se usa en el turno recién generado,
    nunca al re-renderizar el historial (evita repetir la animación en cada rerun)."""
    words = text.split(" ")
    for i in range(0, len(words), chunk_words):
        yield " ".join(words[i : i + chunk_words]) + " "
        time.sleep(delay)


def render_mode_badge(is_mock: bool) -> None:
    """Badge persistente que indica si las respuestas vienen de MockLLMClient o de OCI GenAI real."""
    if is_mock:
        st.markdown(
            '<span class="badge badge-mock" role="status">Modo simulado — sin conexión a OCI GenAI</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge badge-live" role="status">Conectado a OCI Generative AI</span>',
            unsafe_allow_html=True,
        )


def render_confidence(confidence: float) -> None:
    """Renderiza el badge de confianza como pill glass, sin emoji ni colores de sistema."""
    if confidence >= 0.7:
        level, label = "high", "Alta"
    elif confidence >= 0.4:
        level, label = "medium", "Media"
    else:
        level, label = "low", "Baja"
    st.markdown(
        f'<span class="badge badge-{level}" role="status">Confianza {label} · {confidence:.0%}</span>',
        unsafe_allow_html=True,
    )


_ENGINE_LOCK = threading.Lock()
_ENGINE_SINGLETON: RAGEngine | None = None


def load_engine() -> RAGEngine:
    """Carga el RAG Engine una sola vez por proceso, con double-checked locking.

    No usa solo `st.cache_resource`: Streamlit puede ejecutar el script varias
    veces en paralelo (varias reruns casi simultáneas) antes de que el caché
    quede poblado, y cargar bge-m3 más de una vez a la vez en una GPU de VRAM
    limitada puede tumbar el proceso completo sin traceback de Python.
    """
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        with _ENGINE_LOCK:
            if _ENGINE_SINGLETON is None:
                _ENGINE_SINGLETON = RAGEngine()
    return _ENGINE_SINGLETON


with st.sidebar:
    st.markdown(f'<div class="brand-title sidebar">{APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Asistente de Conocimiento Corporativo</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown(
        """<div class="glass-alert">
            <strong>Este es un agente de IA.</strong> Las respuestas se generan automáticamente
            a partir de documentos internos. Verifica siempre la información con el
            área responsable antes de tomar decisiones críticas.
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("Filtrar por área")
    category_options = {"Todas las áreas": None}
    for key, val in BUSINESS_CATEGORIES.items():
        category_options[val["label"]] = key

    selected_category_label = st.selectbox(
        "Categoría de documentos:",
        options=list(category_options.keys()),
        index=0,
    )
    category_filter = category_options[selected_category_label]

    st.divider()

    st.subheader("Stack")
    st.markdown(
        """
    - **LLM**: OCI Generative AI
    - **Embeddings**: BAAI/bge-m3 (local)
    - **Vector Store**: ChromaDB (HNSW)
    - **Orquestación**: LlamaIndex
    """
    )

    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "engine" not in st.session_state:
    st.session_state.engine = load_engine()

st.markdown(f'<div class="brand-title">{APP_NAME}</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="brand-subtitle">Pregunta lo que necesites sobre políticas, procesos y documentos internos de la empresa.</p>',
    unsafe_allow_html=True,
)
render_mode_badge(st.session_state.engine.is_mock)
st.divider()

for i, msg in enumerate(st.session_state.messages):
    avatar = AVATAR_USER if msg["role"] == "user" else AVATAR_ASSISTANT
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("sources"):
            render_sources(msg["sources"])
            render_confidence(msg.get("confidence", 0))

            col1, col2, _ = st.columns([1, 1, 8])
            feedback_key = f"feedback_{i}"
            with col1:
                if st.button("👍", key=f"up_{i}"):
                    st.session_state.feedback[feedback_key] = "positive"
                    save_feedback(msg, "positive")
                    st.toast("Gracias por tu feedback")
            with col2:
                if st.button("👎", key=f"down_{i}"):
                    st.session_state.feedback[feedback_key] = "negative"
                    save_feedback(msg, "negative")
                    st.toast("Gracias, mejoraremos la respuesta")

            if feedback_key in st.session_state.feedback:
                fb = st.session_state.feedback[feedback_key]
                st.caption(f"Feedback registrado: {'Positivo' if fb == 'positive' else 'Negativo'}")

SUGGESTED_QUESTIONS = [
    "¿Cuántos días de vacaciones tengo si llevo 3 años?",
    "¿Cuál es el límite de gastos de transporte?",
    "¿Cómo reporto un incidente P1?",
]

if not st.session_state.messages:
    st.markdown('<p class="caption-text">Prueba con una de estas preguntas:</p>', unsafe_allow_html=True)
    chip_cols = st.columns(len(SUGGESTED_QUESTIONS))
    for col, question in zip(chip_cols, SUGGESTED_QUESTIONS):
        with col:
            if st.button(question, key=f"chip_{question}", use_container_width=True):
                st.session_state.pending_prompt = question
                st.rerun()

prompt = st.chat_input("Escribe tu pregunta...")
if not prompt and st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
        placeholder = st.empty()
        placeholder.markdown(render_skeleton(), unsafe_allow_html=True)

        result = st.session_state.engine.ask(query=prompt, category_filter=category_filter)

        placeholder.empty()
        st.write_stream(stream_response(result["response"]))

        if result["sources"]:
            render_sources(result["sources"])

        render_confidence(result.get("confidence", 0))
        st.caption(f"Respondido en {result['latency_ms']}ms")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["response"],
            "query": prompt,
            "sources": result["sources"],
            "confidence": result["confidence"],
            "latency_ms": result["latency_ms"],
        }
    )
