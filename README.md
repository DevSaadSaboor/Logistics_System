# Logistics Backend

FastAPI backend for a multi-tenant logistics system with tenant management, JWT authentication, shipment tracking, AI-based shipment categorization, and vector-similarity search.

## Overview

This project provides a REST API for:

- managing tenants
- registering and authenticating users per tenant
- creating and tracking shipments with auto-calculated expected delivery dates
- updating shipment status through a defined lifecycle
- categorizing shipments with OpenAI when an API key is configured
- finding similar shipments using pgvector cosine-distance search

The API is built with asynchronous SQLAlchemy sessions and PostgreSQL, and uses Alembic for schema migrations.

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x async |
| Database | PostgreSQL with `asyncpg` |
| Vector Search | `pgvector` + `pgvector[sqlalchemy]` |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | `python-jose` + `passlib[bcrypt]` |
| AI | OpenAI SDK (embeddings + categorization) |
| Retry logic | `tenacity` |
| Testing | `pytest` + `pytest-asyncio` |
| Logging | `python-json-logger` |

## Project Structure

```text
logistics_backend/
├── .env             # (Create this file for local secrets)
├── .env.example     # Environment variable template
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   └── utility.py
│   └── modules/
│       ├── AI/
│       │   └── categorizer.py
│       ├── auth/
│       │   ├── dependencies.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   ├── router.py
│       │   ├── schema.py
│       │   └── service.py
│       ├── shipments/
│       │   ├── ai_service.py
│       │   ├── enum.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   ├── router.py
│       │   ├── schema.py
│       │   └── service.py
│       ├── tenants/
│       │   ├── models.py
│       │   ├── repository.py
│       │   ├── router.py
│       │   ├── schema.py
│       │   └── service.py
│       └── users/
├── migrations/
├── test/
│   └── test_shipmentservice.py
├── test_shipment_schema.py
├── test_shipment_service.py
└── test_shipment_advanced.py
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the provided template to create your `.env` file in the project root:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Ensure your `.env` file contains your real credentials:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/logistics
SECRET_KEY=change-me
OPENAI_API_KEY=sk-...
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Async PostgreSQL connection string |
| `SECRET_KEY` | ✅ | Used for JWT signing |
| `OPENAI_API_KEY` | ❌ | Enables AI categorization and embedding generation |

### 4. Enable pgvector

The `embedding` column uses the `pgvector` PostgreSQL extension. Enable it once in your database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

Swagger docs will be available at `http://127.0.0.1:8000/docs`.

## Docker

You can also run the project with Docker Compose:

```bash
docker compose up --build
```

The compose file starts:

- PostgreSQL on `localhost:5432`
- FastAPI on `localhost:8000`

## Authentication and Tenant Context

This API is multi-tenant. Some endpoints require the `X-Tenant-Slug` header so the request can be resolved to the correct tenant.

Protected endpoints also require a bearer token:

```text
Authorization: Bearer <access_token>
```

**Typical flow:**

1. Create a tenant via `POST /tenants/`.
2. Register a user with that tenant's slug in the `X-Tenant-Slug` header.
3. Log in with the same header to receive an access token.
4. Call protected shipment endpoints with both the bearer token and the tenant header.

## Shipment Lifecycle

Supported statuses and their allowed transitions:

```
CREATED → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED
```

To advance a shipment's status, send a `PATCH` request with the `status` field:

```json
{ "status": "ASSIGNED" }
```

## AI Categorization

When a shipment is created, the API schedules background categorization using the shipment's description. You can also trigger it manually.

**Supported categories:**

| Category | Description |
|---|---|
| `electronics` | Electronic devices and components |
| `perishable` | Food and temperature-sensitive goods |
| `documents` | Paperwork and legal materials |
| `furniture` | Large household or office items |
| `hazardous` | Dangerous or regulated materials |
| `clothing` | Garments and textiles |
| `other` | Default fallback category |

If `OPENAI_API_KEY` is missing or categorization fails, the shipment defaults to `category = "other"` and `confidence = 0.0`. The `ai_processed` flag tracks whether categorization has completed.

## Vector Similarity Search

After a shipment is categorized, the AI service also generates a 1536-dimension OpenAI embedding from the shipment's description and stores it in the `embedding` column (pgvector `vector(1536)` type).

The `/similar` endpoint uses cosine distance (`<=>`) on these embeddings to return the most semantically similar shipments within the same tenant.

**How similarity is calculated:**

```
similarity = 1 - cosine_distance(query_embedding, candidate_embedding)
```

A value of `1.0` means identical, `0.0` means completely unrelated. By default only results with `similarity >= 0.7` are returned.

## API Endpoints

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |

### Tenants

| Method | Path | Description |
|---|---|---|
| `POST` | `/tenants/` | Create a new tenant |
| `GET` | `/tenants/` | List all tenants |
| `DELETE` | `/tenants/{tenant_id}` | Soft-delete a tenant |

### Auth

| Method | Path | Description | Auth required |
|---|---|---|---|
| `POST` | `/auth/register` | Register a user for a tenant | `X-Tenant-Slug` |
| `POST` | `/auth/login` | Log in and receive tokens | `X-Tenant-Slug` |
| `GET` | `/auth/me` | Get current authenticated user | Bearer + `X-Tenant-Slug` |
| `POST` | `/auth/refresh` | Refresh access token | Bearer |

### Shipments

| Method | Path | Description | Auth required |
|---|---|---|---|
| `POST` | `/shipments/` | Create a shipment | Bearer + `X-Tenant-Slug` |
| `PATCH` | `/shipments/{shipment_id}/status` | Update shipment status | Bearer + `X-Tenant-Slug` |
| `GET` | `/shipments/track/{tracking_number}` | Public tracking lookup | — |
| `POST` | `/shipments/{shipment_id}/categorize` | Trigger AI categorization | Bearer + `X-Tenant-Slug` |
| `GET` | `/shipments/{shipment_id}/category` | Get categorization result | Bearer + `X-Tenant-Slug` |
| `GET` | `/shipments/{shipment_id}/similar` | Find similar shipments by embedding | Bearer + `X-Tenant-Slug` |

#### `GET /shipments/{shipment_id}/similar` — Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `min_similarity` | `float` | `0.7` | Minimum cosine similarity score (0.0–1.0) |
| `limit` | `int` | `5` | Maximum number of results to return |
| `offset` | `int` | `0` | Number of results to skip (for pagination) |

#### `GET /shipments/{shipment_id}/similar` — Response

Returns a list of `SimilarShipmentResponse` objects, each containing the matching shipment and its computed similarity score:

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
      "confidence": 0.94,
      ...
    },
    "similarity": 0.9312
  }
]
```

> **Note:** The endpoint only returns results for shipments that have had AI processing completed (i.e. their `embedding` is populated). If the source shipment has no embedding, an empty list is returned.

## Example Payloads

### Create Shipment

The `expected_delivery_date` is **automatically calculated** by the server based on weight, distance (derived from origin/destination), and skipping weekends — you do not need to provide it.

**Request body:**

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

**Response includes the calculated `expected_delivery_date`:**

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
| Distance | Estimated from origin + destination string lengths (15 km/char), 1 day per 100 km |
| Weight | +1 day per every 50 kg |
| Weekends | Saturdays and Sundays are skipped automatically |

**Validation rules:**

- `weight`: must be positive and ≤ 10,000
- `recipient_phone`: digits only, length between 8 and 20
- `description`: minimum 10 characters after trimming whitespace

### Update Shipment Status

```json
{ "status": "PICKED_UP" }
```

## Running Tests

Run all tests:

```bash
pytest -v
```

Run specific test suites:

```bash
# Unit tests inside the test/ package
pytest test/ -v

# Schema validation tests
pytest test_shipment_schema.py -v

# Service-layer unit tests
pytest test_shipment_service.py -v

# Advanced edge-case and AI integration tests
pytest test_shipment_advanced.py -v
```

Run everything at once:

```bash
pytest test/ test_shipment_schema.py test_shipment_service.py test_shipment_advanced.py -v
```

## Notes

- Shipment tracking masks the recipient phone number and returns the full status history.
- Tracking numbers are generated in the format `TRK-XXXXXXXX`.
- Shipment creation automatically writes an initial `CREATED` status log entry.
- `expected_delivery_date` is **auto-calculated** on the server at creation time — clients do not provide it.
- The delivery date calculation skips weekends and factors in shipment weight and estimated distance.
- The `Shipment_Status_Log` table records every status transition with a timestamp, location, and the ID of the user who made the update.
- The `embedding` column is `nullable` — shipments without AI processing simply won't appear as candidates in similarity search results.
- Embeddings are generated using OpenAI's `text-embedding-ada-002` (1536 dimensions) and stored via `pgvector`.

## License

This project is intended for educational and portfolio use.
