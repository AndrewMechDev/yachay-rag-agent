"""Entrypoint de YACHAY para Windows: pre-carga el RAG Engine en el hilo
principal ANTES de arrancar Streamlit, evitando el crash 0xC0000005
(torch + chromadb inicializados fuera del hilo principal, ver
src/engine_singleton.py para el detalle completo del diagnostico).

Uso: python run_app.py
(reemplaza a `streamlit run app/app.py` en Windows)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.engine_singleton import init_engine
from src.logging_config import setup_logging


def main():
    setup_logging()
    print("Pre-cargando YACHAY RAG Engine en el hilo principal...")
    init_engine()
    print("RAG Engine listo. Arrancando Streamlit...\n")

    from streamlit.web import cli as stcli

    app_path = str(Path(__file__).resolve().parent / "app" / "app.py")
    # Reenvía argumentos extra (--server.port, --server.address, etc.) a
    # Streamlit, necesarios para plataformas de deploy que inyectan $PORT.
    sys.argv = ["streamlit", "run", app_path, *sys.argv[1:]]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
