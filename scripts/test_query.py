"""CLI para probar una pregunta sin UI.

Uso: python scripts/test_query.py "¿Cuál es la política de vacaciones?"

Funciona con o sin LLM_API_KEY configurada: si falta, usa MockLLMClient
para validar retrieval + armado de contexto (ver src/generation/llm_client.py).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# La consola de Windows (cp1252) no puede imprimir los emojis de citación que
# devuelve el LLM (📄, etc.) — no es un problema de la respuesta ni del LLM.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.logging_config import setup_logging
from src.rag_engine import RAGEngine


def main():
    setup_logging()

    if len(sys.argv) < 2:
        print('Uso: python scripts/test_query.py "tu pregunta aquí"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"\nPregunta: {query}\n")

    engine = RAGEngine()
    result = engine.ask(query)

    print(f"Respuesta:\n{result['response']}\n")
    print(f"Fuentes ({result['sources_count']}):")
    for s in result["sources"]:
        print(f"  - {s['file']} (cat: {s['category']}, sección: {s['section']}, score: {s['score']})")
    print(f"\nConfianza: {result['confidence']:.0%}")
    print(f"Latencia: {result['latency_ms']}ms")
    print(f"Fallback: {'Sí' if result['fallback_triggered'] else 'No'}")


if __name__ == "__main__":
    main()
