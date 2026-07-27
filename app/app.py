"""Interfaz de chat con Streamlit. Indica que es un agente de IA, muestra fuentes
citadas, permite feedback 👍/👎 e historial por sesión."""

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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()


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
    """Renderiza el expander de fuentes citadas (archivo, categoría, sección, score)."""
    with st.expander(f"📄 Fuentes consultadas ({len(sources)})"):
        for j, src in enumerate(sources, 1):
            st.markdown(
                f"**{j}. {src['file']}** "
                f"(📂 {src['category']} | 📑 Sección: {src['section']} | 🎯 Score: {src['score']})"
            )
            st.caption(src.get("preview", ""))
            st.divider()


def render_confidence(confidence: float) -> None:
    """Renderiza el badge de confianza según el score de validación."""
    if confidence >= 0.7:
        st.success(f"Confianza: {confidence:.0%} ✅")
    elif confidence >= 0.4:
        st.warning(f"Confianza: {confidence:.0%} ⚠️")
    else:
        st.error(f"Confianza: {confidence:.0%} ❌")


@st.cache_resource
def load_engine() -> RAGEngine:
    """Carga el RAG Engine una sola vez por sesión de servidor."""
    return RAGEngine()


with st.sidebar:
    st.title(f"🧠 {APP_NAME}")
    st.caption("Asistente de Conocimiento Corporativo")

    st.divider()

    st.info(
        "⚠️ **Este es un agente de IA**. Las respuestas se generan automáticamente "
        "a partir de documentos internos. Verifica siempre la información con el "
        "área responsable antes de tomar decisiones críticas."
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

    st.subheader("ℹ️ Stack")
    st.markdown(
        """
    - **LLM**: OCI Generative AI
    - **Embeddings**: BAAI/bge-m3 (local)
    - **Vector Store**: ChromaDB (HNSW)
    - **Orquestación**: LlamaIndex
    """
    )

    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "engine" not in st.session_state:
    st.session_state.engine = load_engine()

st.title(f"🧠 {APP_NAME}")
st.markdown("*Pregunta lo que necesites sobre políticas, procesos y documentos internos de la empresa.*")
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
                    st.toast("¡Gracias por tu feedback!")
            with col2:
                if st.button("👎", key=f"down_{i}"):
                    st.session_state.feedback[feedback_key] = "negative"
                    save_feedback(msg, "negative")
                    st.toast("Gracias. Mejoraremos la respuesta.")

            if feedback_key in st.session_state.feedback:
                fb = st.session_state.feedback[feedback_key]
                st.caption(f"Feedback registrado: {'👍 Positivo' if fb == 'positive' else '👎 Negativo'}")

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
        st.caption(f"⏱️ Respondido en {result['latency_ms']}ms")

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
