<div align="center">

# 🚚 Logistics Backend

**A production-ready, multi-tenant logistics REST API built with FastAPI, PostgreSQL, and AI-powered features.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![License](https://img.shields.io/badge/License-Educational-blue?style=flat)](#license)

[Features](#features) · [Tech Stack](#tech-stack) · [Project Structure](#project-structure) · [Setup](#setup) · [API Reference](#api-endpoints) · [Testing](#running-tests)

</div>

---

## Overview

A robust REST API for managing multi-tenant logistics operations. It handles tenant provisioning, user authentication, shipment lifecycle tracking, AI-powered categorization, semantic vector search, and a RAG-based Q&A assistant grounded in company policy documents.

---

## Features

- 🏢 **Multi-tenant architecture** — fully isolated data per tenant with role-based access control
- 🔐 **JWT authentication** — secure bearer tokens with refresh support and per-tenant scoping
- 📦 **Shipment lifecycle** — full status tracking from creation to delivery with audit log
- 🤖 **AI categorization** — automatic shipment classification via GPT-4o-mini with retry logic
- 🔍 **Vector similarity search** — find semantically similar shipments using pgvector cosine distance
- 📍 **Smart delivery estimation** — real geocoding (Nominatim + Haversine formula), weight surcharges, weekend skipping
- 💬 **RAG Q&A assistant** — answer policy questions grounded exclusively in your company knowledge base
- 🧪 **Comprehensive test suite** — pytest + AsyncMock, no real database required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async) |
| Database | PostgreSQL + asyncpg |
| Vector Search | pgvector |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Authentication | python-jose + passlib[bcrypt] |
| AI — Categorization | OpenAI SDK (`gpt-4o-mini`) |
| AI — Embeddings | OpenAI SDK (`text-embedding-3-small`) |
| Geocoding | geopy (Nominatim + Haversine) |
| RAG Pipeline | LangChain + LangChain-OpenAI + PGVector |
| Retry Logic | tenacity |
| Testing | pytest + pytest-asyncio |

---

## Project Structure

```
logistics_backend/
├── .env                        # Local secrets (create from env.example)
├── env.example                 # Environment variable template
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
├── data/
│   └── logistics_docs.txt      # Company knowledge base for RAG assistant
└── app/
    ├── main.py
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   ├── dependencies.py
    │   ├── security.py
    │   └── utility.py
    └── modules/
        ├── AI/
        │   ├── categorizer.py       # OpenAI shipment categorizer
        │   ├── knowledge_loader.py  # Loads and chunks logistics_docs.txt
        │   ├── rag_service.py       # RAG pipeline (retrieve → generate)
        │   ├── router.py            # POST /ai/ask endpoint
        │   └── vector_store.py      # PGVector store setup and ingestion
        ├── auth/                    # JWT auth — register, login, refresh
        ├── shipments/               # Shipment CRUD, AI service, similarity search
        ├── tenants/                 # Tenant management
        └── users/                   # User management
```

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
# macOS / Linux
cp env.example .env

# Windows
copy env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/logistics
SECRET_KEY=change-me
OPENAI_API_KEY=sk-...        # Optional — enables AI features
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Async PostgreSQL connection string |
| `SECRET_KEY` | ✅ | Secret key used for JWT signing |
| `OPENAI_API_KEY` | ❌ | Enables AI categorization, embeddings, and the RAG assistant |

### 4. Enable the pgvector extension

Run this once in your PostgreSQL database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Ingest company knowledge (RAG assistant)

Before the `/ai/ask` endpoint can answer questions, run the ingestion script once to chunk and store `data/logistics_docs.txt` in the PGVector collection:

```bash
python -c "from app.modules.AI.vector_store import create_vector_store; create_vector_store()"
```

> Re-run this whenever `logistics_docs.txt` is updated.

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

Swagger UI will be available at **http://127.0.0.1:8000/docs**

---

## Docker

Start both PostgreSQL and FastAPI with a single command:

```bash
docker compose up --build
```

| Service | Host |
|---|---|
| PostgreSQL | `localhost:5432` |
| FastAPI | `localhost:8000` |

---

## Authentication & Tenant Context

This API is **multi-tenant**. Tenant-scoped endpoints require the `X-Tenant-Slug` header to resolve the correct tenant context.

Protected endpoints also require a bearer token:

```
Authorization: Bearer <access_token>
X-Tenant-Slug: your-tenant-slug
```

If the authenticated user does not belong to the tenant resolved from `X-Tenant-Slug`, the API returns `403 Forbidden`.

**Typical authentication flow:**

1. `POST /tenants/` — create a tenant
2. `POST /auth/register` — register a user (include `X-Tenant-Slug`)
3. `POST /auth/login` — receive an access token
4. Call protected endpoints with both `Authorization` and `X-Tenant-Slug` headers

---

## Shipment Lifecycle

Shipments progress through a strict set of status transitions:

```
CREATED → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED
```

To advance a shipment's status, send a `PATCH` request:

```json
{ "status": "ASSIGNED" }
```

---

## AI Features

### Shipment Categorization

When a shipment is created, categorization is scheduled in the background using the shipment's description. It can also be triggered manually via `POST /shipments/{id}/categorize`.

**Model:** `gpt-4o-mini`

| Category | Description |
|---|---|
| `electronics` | Electronic devices and components |
| `perishable` | Food and temperature-sensitive goods |
| `documents` | Paperwork and legal materials |
| `furniture` | Large household or office items |
| `hazardous` | Dangerous or regulated materials |
| `clothing` | Garments and textiles |
| `other` | Default fallback |

If `OPENAI_API_KEY` is absent or categorization fails, the shipment defaults to `category = "other"` and `confidence = 0.0`. Failed calls are retried up to 3 times with exponential back-off via `tenacity`.

### Vector Similarity Search

After categorization, a 1536-dimension embedding is generated from the shipment description using `text-embedding-3-small` and stored via pgvector.

The `/similar` endpoint uses cosine distance to return semantically similar shipments within the same tenant:

```
similarity = 1 − cosine_distance(query_embedding, candidate_embedding)
```

A score of `1.0` = identical; `0.0` = completely unrelated. Only results with `similarity ≥ 0.7` are returned by default.

**Query parameters for `/shipments/{id}/similar`:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `min_similarity` | float | `0.7` | Minimum cosine similarity threshold |
| `limit` | int | `5` | Maximum number of results |
| `offset` | int | `0` | Pagination offset |

### RAG Q&A Assistant

The `/ai/ask` endpoint answers natural-language questions about company policy, grounded exclusively in `data/logistics_docs.txt`.

**How it works:**
1. The question is embedded with `text-embedding-3-small`
2. The top-3 most relevant document chunks are retrieved from PGVector
3. Those chunks are passed as context to `gpt-4o-mini` to generate a grounded answer

If the answer isn't in the knowledge base, the model responds: *"I don't know based on company policy."*

---

## API Endpoints

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |

### Tenants

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/tenants/` | Create a tenant | Bearer (admin) |
| `GET` | `/tenants/` | List all tenants | Bearer (admin) |
| `DELETE` | `/tenants/{tenant_id}` | Soft-delete a tenant | Bearer (admin) |

### Auth

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Register a user | `X-Tenant-Slug` |
| `POST` | `/auth/login` | Log in and receive tokens | `X-Tenant-Slug` |
| `GET` | `/auth/me` | Get the current user | Bearer |
| `POST` | `/auth/refresh` | Refresh access token | `X-Tenant-Slug` |

### Shipments

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/shipments/` | Create a shipment | Bearer (admin/operator) + `X-Tenant-Slug` |
| `PATCH` | `/shipments/{id}/status` | Update status | Bearer (admin/operator) + `X-Tenant-Slug` |
| `GET` | `/shipments/track/{tracking_number}` | Public tracking lookup | — |
| `POST` | `/shipments/{id}/categorize` | Trigger AI categorization | Bearer (admin/operator) + `X-Tenant-Slug` |
| `GET` | `/shipments/{id}/category` | Get categorization result | Bearer (any role) + `X-Tenant-Slug` |
| `GET` | `/shipments/{id}/similar` | Find similar shipments | Bearer (any role) + `X-Tenant-Slug` |

### AI Assistant

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/ai/ask` | Ask a policy or logistics question | — |
| `POST` | `/ai/search` | Semantic search over knowledge base | — |

---

## Example Payloads

### Create a Shipment

> `expected_delivery_date` is calculated automatically — do not provide it.

**Request:**
```json
{
  "origin": "Karachi",
  "destination": "Lahore",
  "recipient_name": "Ali Khan",
  "recipient_phone": "03001234567",
  "weight": 12.5,
  "delivery_address": "Street 10, Lahore",
  "pickup_date": "2026-04-08T09:00:00Z",
  "description": "Two sealed boxes containing office electronics"
}
```

**Response:**
```json
{
  "id": "...",
  "tracking_number": "TRK-ABCD1234",
  "status": "CREATED",
  "origin": "Karachi",
  "destination": "Lahore",
  "recipient_name": "Ali Khan",
  "recipient_phone": "03001234567",
  "weight": 12.5,
  "delivery_address": "Street 10, Lahore",
  "pickup_date": "2026-04-08T09:00:00Z",
  "expected_delivery_date": "2026-04-10T09:00:00Z",
  "description": "Two sealed boxes containing office electronics",
  "category": "other",
  "confidence": 0.0
}
```

**Delivery date calculation logic:**

| Factor | Rule |
|---|---|
| Distance | Real coordinates from Nominatim; great-circle distance via Haversine formula. Falls back to 100 km if geocoding fails. |
| Base transit days | 1 day per 400 km (minimum 1 day) |
| Weight surcharge | +1 day per 50 kg |
| Weekends | Saturdays and Sundays are automatically skipped |

**Validation rules:**

- `weight` — must be positive and ≤ 10,000
- `recipient_phone` — digits only, 8–20 characters
- `description` — minimum 10 characters after trimming whitespace

### Update Shipment Status

```json
{ "status": "PICKED_UP" }
```

### Ask the RAG Assistant

**Request:**
```json
{ "question": "What is the standard delivery SLA?" }
```

**Response:**
```json
{
  "answer": "Standard delivery takes 3–5 business days depending on distance and weight.",
  "sources": ["Delivery SLA Policy"]
}
```

---

## Error Semantics

| Status Code | Meaning |
|---|---|
| `400 Bad Request` | Validation or business-rule conflict (e.g. duplicate tenant, duplicate user) |
| `401 Unauthorized` | Invalid or missing JWT / login credentials |
| `403 Forbidden` | Valid user without required role, or tenant mismatch |
| `404 Not Found` | Tenant or shipment not found in the current context |

---

## Running Tests

All tests are in the `test/` directory and use `pytest` with `AsyncMock` for async service isolation. No live database is required.

| File | Coverage |
|---|---|
| `test_shipment_schema.py` | Pydantic validation — valid creation, invalid weight/phone/description |
| `test_shipment_service.py` | Service layer — create, update status, assign driver, tracking lookup |
| `test_shipment_advanced.py` | Edge cases — boundary values, ORM serialization, tracking format, AI categorization, phone masking, status history |

```bash
# Run all tests
pytest test/ -v

# Run a specific suite
pytest test/test_shipment_schema.py -v
pytest test/test_shipment_service.py -v
pytest test/test_shipment_advanced.py -v
```

---

## Notes

- Tracking numbers are generated in the format `TRK-XXXXXXXX`
- Shipment creation automatically writes an initial `CREATED` entry to the status log
- The `Shipment_Status_Log` table records every status transition with a timestamp, location, and the ID of the acting user
- The recipient phone number is masked in public tracking responses
- The `embedding` column is nullable — shipments without AI processing are excluded from similarity search results
- The RAG assistant uses a separate PGVector collection (`logistics_docs`) populated from `data/logistics_docs.txt`. Re-run the ingestion script whenever that file is updated

---

## License

This project is intended for **educational and portfolio use**.
