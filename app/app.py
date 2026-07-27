"""Interfaz de chat con Streamlit. Sistema visual glassmorphism (ver skill
yachay-ui-streamlit). Indica que es un agente de IA, muestra fuentes citadas,
permite feedback e historial por sesión."""

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import APP_NAME, BUSINESS_CATEGORIES
from src.logging_config import setup_logging
from src.rag_engine import RAGEngine

st.set_page_config(
    page_title=f"{APP_NAME} — Asistente de Conocimiento Corporativo",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()

THEME_CSS = """
<style>
.stApp {
    background: radial-gradient(circle at top left, #1b2140 0%, #0B0F1A 55%, #05070c 100%);
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}

[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 14px;
}

[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(212, 168, 85, 0.35);
    border-radius: 14px;
}

div.stButton > button {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    color: #EDEBFF;
    transition: border-color 0.2s ease, color 0.2s ease;
}
div.stButton > button:hover {
    border-color: #D4A855;
    color: #D4A855;
}

.brand-title {
    font-size: 2.3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #D4A855, #EDEBFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.brand-title.sidebar {
    font-size: 1.5rem;
}
.brand-subtitle {
    color: rgba(237, 235, 255, 0.65);
    margin-top: 0.1rem;
}

.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
}

.glass-alert {
    background: rgba(212, 168, 85, 0.08);
    backdrop-filter: blur(12px);
    border-left: 3px solid #D4A855;
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    font-size: 0.9rem;
    color: #EDEBFF;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
.badge-high { background: rgba(94, 219, 138, 0.15); color: #6EE7A8; border-color: rgba(94, 219, 138, 0.4); }
.badge-medium { background: rgba(212, 168, 85, 0.15); color: #D4A855; border-color: rgba(212, 168, 85, 0.4); }
.badge-low { background: rgba(224, 92, 92, 0.15); color: #F08787; border-color: rgba(224, 92, 92, 0.4); }

.source-title { font-weight: 600; color: #EDEBFF; }
.source-meta { color: rgba(237, 235, 255, 0.6); font-size: 0.85rem; }

h1, h2, h3 { color: #EDEBFF !important; }
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
    """Renderiza el expander de fuentes citadas como glass cards."""
    with st.expander(f"Fuentes consultadas ({len(sources)})"):
        for j, src in enumerate(sources, 1):
            st.markdown(
                f"""<div class="glass-card">
                    <div class="source-title">{j}. {src['file']}</div>
                    <div class="source-meta">Categoría: {src['category']} · Sección: {src['section']} · Score: {src['score']}</div>
                    <div class="source-meta">{src.get('preview', '')}</div>
                </div>""",
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
        f'<span class="badge badge-{level}">Confianza {label} · {confidence:.0%}</span>',
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_engine() -> RAGEngine:
    """Carga el RAG Engine una sola vez por sesión de servidor."""
    return RAGEngine()


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
st.divider()

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
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

if prompt := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en documentos internos..."):
            result = st.session_state.engine.ask(query=prompt, category_filter=category_filter)

        st.markdown(result["response"])

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
