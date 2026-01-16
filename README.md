# Monetra AI

Natural-language transaction assistant backed by vector search. This service parses user queries ("how much did I spend on food?") into structured intent, retrieves relevant transactions from Qdrant, and returns resolved categories or formatted spending summaries. It includes a Kafka consumer for indexing new transactions into Qdrant.

## What this does

- Accepts natural language finance queries over HTTP
- Uses an LLM (Groq or Ollama) to parse intent and target (category/merchant/memo)
- Retrieves relevant transactions via embeddings + Qdrant
- Streams formatted spending summaries
- Consumes Kafka events to index transactions into Qdrant

## Tech stack

- FastAPI API service
- Qdrant vector database
- LLM providers: Groq (cloud) or Ollama (local)
- Embeddings: Google or Ollama
- Kafka consumer for ingestion

## Project layout

- `main.py` FastAPI app
- `api/` HTTP routes and request models
- `services/` service layer
- `nl/` prompt + LLM parsing
- `rag/` embeddings, indexing, and retrieval
- `consumer.py` Kafka consumer
- `run_service/run.py` ingestion worker
- `config/` settings and topics

## Requirements

- Python 3.11.9
- Qdrant running locally or remotely
- Kafka (for ingestion worker)
- Groq API key (prod) or Ollama running locally (dev)

## Setup

Using Poetry:

```bash
poetry install --no-root
```

Create `.env`:

```bash
cp .env.example .env
```

If you don’t have `.env.example`, create `.env` with the variables below.

## Environment variables

Required values depend on your environment. Typical values:

```
# App
ENVIRONMENT=dev
BACKEND_HEADER=your-shared-secret

# LLM
GROQ_API_KEY=your-groq-key
LLM_MODEL_NAME=llama-3.1-8b-instant

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=monetra_collection

# Embeddings
EMBEDDING_MODEL_PROVIDER=ollama   # or google
GOOGLE_EM_API_KEY=

# Kafka (prod)
KAFKA_URL=
KAFKA_GROUP_ID=monetra-ai
KAFKA_PEM=
KAFKA_SERVICE_CERT=
KAFKA_SERVICE_KEY=
```

Notes:

- In `dev`, Groq and Kafka are optional if you use Ollama + local testing.
- `KAFKA_*` values are base64 strings for certificates.

## Run the API

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Remember to pass the backend header on requests:

```
monetra-ai-key: <BACKEND_HEADER>
```

## Run the ingestion worker

```bash
poetry run python run_service/run.py
```

This listens to the `transaction.created.*` Kafka topic and indexes transactions into Qdrant.

## API examples

Resolve a query:

```bash
curl -X POST http://localhost:8000/nl/resolve \
  -H "Content-Type: application/json" \
  -H "monetra-ai-key: $BACKEND_HEADER" \
  -d '{"user_id": 123, "query": "how much did i spend on groceries"}'
```

Format a price:

```bash
curl -X POST http://localhost:8000/nl/format \
  -H "Content-Type: application/json" \
  -H "monetra-ai-key: $BACKEND_HEADER" \
  -d '{"amount": 50.86, "category": "transport", "currency": "USD"}'
```

## Docker

Build:

```bash
docker build -t monetra-ai .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env monetra-ai
```

## Development notes

- The API enforces `monetra-ai-key` for every request.
- Qdrant must be reachable from the API.
- For Ollama, ensure the model is pulled and the server runs on `http://localhost:11434`.

## Troubleshooting

- Qdrant errors: confirm `QDRANT_URL` and `QDRANT_COLLECTION_NAME`.
- LLM errors: check `GROQ_API_KEY` or Ollama availability.
- Kafka errors: verify certificates and topic names.
