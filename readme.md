<div align="center">

# 🚚 Logistics Backend

**A production-grade, multi-tenant logistics REST API with AI-powered shipment intelligence**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-Educational-green?style=for-the-badge)](#-license)

*JWT auth · Multi-tenancy · Vector similarity search · RAG Q&A · LangGraph agentic assistant*

</div>

---

## 📋 Table of Contents

- [🌐 Overview](#-overview)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Setup & Installation](#-setup--installation)
- [🐳 Docker](#-docker)
- [🔐 Authentication & Tenant Context](#-authentication--tenant-context)
- [🔄 Shipment Lifecycle](#-shipment-lifecycle)
- [🤖 AI Features](#-ai-features)
  - [AI Categorization](#ai-categorization)
  - [Vector Similarity Search](#vector-similarity-search)
  - [RAG Q&A Assistant](#rag-qa-assistant)
  - [LangGraph Agentic Assistant](#langgraph-agentic-assistant)
- [📡 API Reference](#-api-reference)
- [🚦 Error Handling](#-error-handling)
- [📝 Example Payloads](#-example-payloads)
- [🧪 Running Tests](#-running-tests)
- [📌 Notes](#-notes)
- [📄 License](#-license)

---

## 🌐 Overview

This project provides a REST API for:

| Feature | Description |
|---|---|
| 🏢 **Multi-Tenancy** | Full tenant isolation with slug-based routing, soft-delete, and RBAC |
| 🔑 **JWT Auth** | Register & authenticate users per tenant with access + refresh token flow |
| 📦 **Shipment Tracking** | Create & track shipments with auto-calculated delivery dates |
| 🔄 **Lifecycle Management** | Advance shipment status through a strict defined pipeline |
| 🤖 **AI Categorization** | Auto-classify shipments by description using `gpt-4o-mini` |
| 🔍 **Vector Search** | Find semantically similar shipments via pgvector cosine distance |
| 💬 **RAG Assistant** | Answer policy questions grounded exclusively in your knowledge base |
| 🧠 **LangGraph Agent** | Intent-aware stateful graph: classify → retrieve → generate |
| 📐 **Auto Delivery Dates** | Haversine geocoding + weight surcharges + weekend skipping |

> Built with async SQLAlchemy + PostgreSQL. Schema migrations managed by Alembic.

---

## 🛠️ Tech Stack

<details>
<summary><strong>View full technology stack</strong></summary>

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x async |
| Database | PostgreSQL + `asyncpg` |
| Vector Search | `pgvector` (SQLAlchemy integration) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | `python-jose` + `passlib[bcrypt]` |
| AI — Categorization | OpenAI SDK — `gpt-4o-mini` |
| AI — Embeddings | OpenAI SDK — `text-embedding-3-small` |
| Geocoding / Distance | `geopy` (Nominatim + Haversine) |
| RAG | `langchain-community` + `langchain-openai` + `langchain-text-splitters` |
| Agentic AI | `langgraph` — stateful classify → retrieve → generate graph |
| RAG Vector Store | PGVector via `psycopg2-binary` |
| Retry Logic | `tenacity` (exponential back-off, up to 3 retries) |
| Linting | `ruff` |
| Testing | `pytest` + `pytest-asyncio` |

</details>

---

## 📁 Project Structure

<details>
<summary><strong>Expand file tree</strong></summary>

```text
logistics_backend/
├── .env                          # Local secrets (create from env.example)
├── env.example                   # Environment variable template
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
├── data/
│   └── logistics_docs.txt        # Company knowledge base for the RAG assistant
├── app/
│   ├── main.py                   # FastAPI app, routers, exception handlers
│   ├── core/
│   │   ├── base.py
│   │   ├── config.py             # Settings loaded from .env
│   │   ├── database.py           # Async engine + session factory
│   │   ├── dependencies.py       # Shared FastAPI dependencies
│   │   ├── exceptions.py         # Custom exception classes + global handlers
│   │   ├── logging.py            # Structured logger setup
│   │   ├── security.py           # JWT + password hashing
│   │   └── utility.py
│   ├── shared/
│   │   ├── base_model.py         # SQLAlchemy base model with UUID PK
│   │   └── enums.py              # Shared enums (e.g. UserRole)
│   └── modules/
│       ├── AI/
│       │   ├── Langgraph/
│       │   │   ├── graph.py      # StateGraph: classify → retrieve → generate
│       │   │   ├── node.py       # classify_node, retriever_node, generate_node
│       │   │   ├── state.py      # AgentState TypedDict
│       │   │   └── memory.py     # Session memory (reserved for future multi-turn)
│       │   ├── categorizer.py    # OpenAI shipment categorizer
│       │   ├── knowledge_loader.py # Loads and chunks logistics_docs.txt
│       │   ├── rag_service.py    # RAG pipeline (retrieve → generate)
│       │   ├── router.py         # /ai/ask  /ai/search  /ai/assistant
│       │   ├── schema.py         # AssistantRequest / AssistantResponse schemas
│       │   └── vector_store.py   # PGVector store setup and ingestion
│       ├── auth/                 # Refresh token management, /auth/me
│       ├── shipments/            # CRUD, status lifecycle, AI service
│       ├── tenants/              # Tenant CRUD + soft-delete
│       └── users/                # Registration, login, token refresh
├── migrations/
└── test/
    ├── conftest.py
    ├── test_shipment_advanced.py
    ├── test_shipment_schema.py
    └── test_shipment_service.py
```

</details>

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL with the `pgvector` extension
- An OpenAI API key *(optional — enables all AI features)*

---

<details>
<summary><strong>Step 1 — Create and activate a virtual environment</strong></summary>

```bash
python -m venv venv
```

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

</details>

---

<details>
<summary><strong>Step 2 — Install dependencies</strong></summary>

```bash
pip install -r requirements.txt
```

</details>

---

<details>
<summary><strong>Step 3 — Configure environment variables</strong></summary>

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
OPENAI_API_KEY=sk-...
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Async PostgreSQL connection string |
| `SECRET_KEY` | ✅ | Used for JWT signing |
| `OPENAI_API_KEY` | ❌ | Enables AI categorization, embeddings, RAG, and LangGraph |

</details>

---

<details>
<summary><strong>Step 4 — Enable pgvector extension</strong></summary>

Run once in your PostgreSQL database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

</details>

---

<details>
<summary><strong>Step 5 — Run database migrations</strong></summary>

```bash
alembic upgrade head
```

</details>

---

<details>
<summary><strong>Step 6 — Ingest the company knowledge base (RAG)</strong></summary>

Run once before using `/ai/ask` or `/ai/assistant`. Re-run whenever `data/logistics_docs.txt` is updated.

```bash
python -c "from app.modules.AI.vector_store import create_vector_store; create_vector_store()"
```

</details>

---

<details>
<summary><strong>Step 7 — Start the API server</strong></summary>

```bash
uvicorn app.main:app --reload
```

Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

</details>

---

## 🐳 Docker

Spin up the full stack (PostgreSQL + FastAPI) with a single command:

```bash
docker compose up --build
```

| Service | Port |
|---|---|
| FastAPI | `localhost:8000` |
| PostgreSQL | `localhost:5432` |

---

## 🔐 Authentication & Tenant Context

This API is **multi-tenant**. Tenant-scoped endpoints require the `X-Tenant-Slug` header, and protected endpoints require a bearer token:

```http
Authorization: Bearer <access_token>
X-Tenant-Slug: my-company
```

Tenant-scoped endpoints enforce:
- ✅ The authenticated user belongs to the tenant resolved from `X-Tenant-Slug`
- ✅ Role-based access control (RBAC) per endpoint

**Typical flow:**

```
1. POST /tenants/          → create a tenant
2. POST /auth/register     → register a user (X-Tenant-Slug required)
3. POST /auth/login        → receive access_token + refresh_token
4. Call shipment endpoints → Bearer token + X-Tenant-Slug
5. POST /auth/refresh      → renew access_token when it expires
```

> If the token's tenant and `X-Tenant-Slug` don't match, the API returns `403 Forbidden`.

---

## 🔄 Shipment Lifecycle

Shipments progress through a strict, one-directional state machine:

```
CREATED → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED
```

Advance a shipment's status with a `PATCH` request:

```json
{ "status": "ASSIGNED" }
```

Every transition is recorded in the `Shipment_Status_Log` table with a timestamp, location, and the acting user's ID.

---

## 🤖 AI Features

### AI Categorization

Shipments are categorized automatically in the background on creation, or triggered manually via `POST /shipments/{id}/categorize`.

**Model:** `gpt-4o-mini` · **Retry:** up to 3× with exponential back-off via `tenacity`

| Category | Description |
|---|---|
| `electronics` | Electronic devices and components |
| `perishable` | Food and temperature-sensitive goods |
| `documents` | Paperwork and legal materials |
| `furniture` | Large household or office items |
| `hazardous` | Dangerous or regulated materials |
| `clothing` | Garments and textiles |
| `other` | Default fallback |

> If `OPENAI_API_KEY` is absent or categorization fails, the shipment defaults to `category = "other"` and `confidence = 0.0`. The `ai_processed` flag tracks whether categorization has completed.

---

### Vector Similarity Search

After categorization, a **1536-dimension embedding** is generated from the shipment description using `text-embedding-3-small` and stored in the `embedding` pgvector column (`vector(1536)`).

The `/similar` endpoint returns semantically similar shipments within the same tenant using **cosine distance**:

```
similarity = 1 − cosine_distance(query_embedding, candidate_embedding)
```

| Score | Meaning |
|---|---|
| `1.0` | Identical |
| `≥ 0.7` | Default minimum threshold |
| `0.0` | Completely unrelated |

> Only shipments with a populated `embedding` (i.e., AI-processed) appear as candidates.

---

### RAG Q&A Assistant

`POST /ai/ask` answers natural-language questions grounded **exclusively** in `data/logistics_docs.txt` — the model won't hallucinate outside that context.

**Pipeline:**

```
User question
     ↓
Embed with text-embedding-3-small
     ↓
Retrieve top-3 chunks from PGVector (logistics_docs collection)
     ↓
Generate grounded answer with gpt-4o-mini
     ↓
Return answer + source section headings
```

> If the answer isn't covered by the knowledge base, the model replies: *"I don't know based on company policy."*

---

### LangGraph Agentic Assistant

`POST /ai/assistant` runs a **stateful LangGraph graph** with intent classification — more intelligent than the plain RAG pipeline.

**Graph flow:**

```
[classify] → [retriever] → [generate] → END
```

| Node | Responsibility |
|---|---|
| `classify` | Detects intent: `shipment` or `policy` |
| `retriever` | Semantic search + query expansion for delay/lateness queries + keyword re-ranking |
| `generate` | Calls `gpt-4o-mini` with retrieved context to produce a grounded answer |

<details>
<summary><strong>AgentState fields</strong></summary>

| Field | Type | Description |
|---|---|---|
| `question` | `str` | The user's question |
| `session_id` | `str \| None` | Optional session ID for future multi-turn memory |
| `messages` | `list[dict]` | Conversation history (reserved) |
| `intent` | `str \| None` | Classified intent: `shipment` or `policy` |
| `context` | `str \| None` | Retrieved document context passed to the generator |
| `answer` | `str \| None` | Final generated answer |

</details>

> The graph is compiled per-request via `build_graph(db)` so the async DB session is correctly scoped to each request lifecycle.

---

## 📡 API Reference

### 🏥 Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |

### 🏢 Tenants

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/tenants/` | Create a tenant | Bearer (`admin`) |
| `GET` | `/tenants/` | List all tenants | Bearer (`admin`) |
| `DELETE` | `/tenants/{tenant_id}` | Soft-delete a tenant | Bearer (`admin`) |

### 🔑 Auth

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Register a user | `X-Tenant-Slug` |
| `POST` | `/auth/login` | Login → access + refresh tokens | `X-Tenant-Slug` |
| `GET` | `/auth/me` | Get current user | Bearer |
| `POST` | `/auth/refresh` | Refresh access token | `X-Tenant-Slug` |

### 📦 Shipments

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/shipments/` | Create a shipment | Bearer (`admin`/`operator`) + Slug |
| `PATCH` | `/shipments/{id}/status` | Update status | Bearer (`admin`/`operator`) + Slug |
| `GET` | `/shipments/track/{tracking_number}` | Public tracking lookup | — |
| `POST` | `/shipments/{id}/categorize` | Trigger AI categorization | Bearer (`admin`/`operator`) + Slug |
| `GET` | `/shipments/{id}/category` | Get categorization result | Bearer (any role) + Slug |
| `GET` | `/shipments/{id}/similar` | Find similar shipments | Bearer (any role) + Slug |

<details>
<summary><strong>GET /shipments/{id}/similar — query parameters & response</strong></summary>

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `min_similarity` | `float` | `0.7` | Minimum cosine similarity (0.0–1.0) |
| `limit` | `int` | `5` | Max results to return |
| `offset` | `int` | `0` | Pagination offset |

**Response:**

```json
[
  {
    "shipment": {
      "id": "...",
      "tracking_number": "TRK-ABCD1234",
      "status": "IN_TRANSIT",
      "origin": "Karachi",
      "destination": "Lahore",
      "category": "electronics",
      "confidence": 0.94
    },
    "similarity": 0.9312
  }
]
```

</details>

### 🧠 AI Assistant

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/ai/ask` | RAG Q&A grounded in the knowledge base | — |
| `POST` | `/ai/search` | Semantic document search | — |
| `POST` | `/ai/assistant` | LangGraph agentic assistant | — |

---

## 🚦 Error Handling

All error responses follow a consistent JSON envelope:

```json
{
  "success": false,
  "error": "<message>"
}
```

| Status | When |
|---|---|
| `400 Bad Request` | Business rule conflict (e.g. duplicate tenant or user) |
| `401 Unauthorized` | Invalid or missing JWT / credentials |
| `403 Forbidden` | Insufficient role, or tenant mismatch |
| `404 Not Found` | Tenant or shipment not found in context |
| `422 Unprocessable Entity` | Pydantic request validation failure |

**Common error messages:**

- `Unauthorized: invalid access token`
- `Forbidden: insufficient role permissions`
- `Forbidden: user does not belong to requested tenant`
- `Tenant not found for provided X-Tenant-Slug`
- `Shipment not found`

---

## 📝 Example Payloads

<details>
<summary><strong>Create Shipment</strong></summary>

> `expected_delivery_date` is **auto-calculated** by the server — do not provide it.

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

**Delivery date calculation:**

| Factor | Rule |
|---|---|
| Distance | Real coordinates via Geopy (Nominatim) + Haversine formula. Fallback: 100 km |
| Base transit | 1 day per 400 km (minimum 1 day) |
| Weight surcharge | +1 day per 50 kg |
| Weekends | Saturdays and Sundays skipped automatically |

**Validation rules:**

| Field | Rule |
|---|---|
| `weight` | Must be positive and ≤ 10,000 |
| `recipient_phone` | Digits only, length 8–20 |
| `description` | Minimum 10 characters after trimming whitespace |

</details>

---

<details>
<summary><strong>Update Shipment Status</strong></summary>

```json
{ "status": "PICKED_UP" }
```

</details>

---

<details>
<summary><strong>POST /ai/ask — RAG Q&A</strong></summary>

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

</details>

---

<details>
<summary><strong>POST /ai/assistant — LangGraph Agent</strong></summary>

**Request:**
```json
{
  "query": "Why is my shipment delayed?",
  "session_id": "user-abc-123"
}
```

**Response:**
```json
{
  "answer": "Shipment delays may occur due to customs clearance, weather conditions, or high volume periods. Please contact support with your tracking number for a specific update."
}
```

</details>

---

## 🧪 Running Tests

All tests use `unittest` + `pytest` with `AsyncMock` — no real database required.

```bash
# Run all tests
pytest test/ -v

# Run a specific suite
pytest test/test_shipment_schema.py -v
pytest test/test_shipment_service.py -v
pytest test/test_shipment_advanced.py -v
```

| File | Coverage |
|---|---|
| `test_shipment_schema.py` | Pydantic validation — valid creation, invalid weight / phone / description |
| `test_shipment_service.py` | Service layer — create, update status, assign driver, tracking lookup (found & not-found) |
| `test_shipment_advanced.py` | Edge cases — boundary values, ORM serialization, tracking format & uniqueness, AI categorization success & fallback, phone masking, multi-entry status history, user_id forwarding |

---

## 📌 Notes

- Tracking numbers are generated in the format `TRK-XXXXXXXX`
- The recipient phone number is **masked** in public tracking responses
- Every status transition is logged to `Shipment_Status_Log` with timestamp, location, and user ID
- The `embedding` column is nullable (`pgvector(1536)`) — shipments without AI processing are excluded from similarity results
- The LangGraph graph is compiled **per-request** via `build_graph(db)` so the async DB session is properly scoped
- The RAG assistant uses a **separate** PGVector collection (`logistics_docs`) — re-run the ingestion script whenever `logistics_docs.txt` is updated
- Structured logging follows the pattern `module.action.event key=value` throughout for easy log parsing and filtering
- `app/shared/` contains cross-cutting base models and enums reused across all domain modules

---

## 📄 License

<div align="center">

This project is intended for **educational and portfolio use**.

</div>