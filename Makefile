.PHONY: setup ingest run test docker-build docker-run clean

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Entorno listo. Edita .env con tu API Key de OCI GenAI."

ingest:
	python scripts/ingest_documents.py

run:
	streamlit run app/app.py

test:
	pytest tests/ -v

docker-build:
	docker build -t yachay-rag-agent:latest .

docker-run:
	docker run -d --name yachay -p 8501:8501 --env-file .env yachay-rag-agent:latest

clean:
	rm -rf chroma_db/* logs/*
