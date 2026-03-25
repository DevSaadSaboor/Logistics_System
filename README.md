<p align="center">
  <h1 align="center">📦 Logistics System — Backend API</h1>
  <p align="center">
    A multi-tenant logistics and shipment management REST API built with FastAPI, SQLAlchemy, and PostgreSQL.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.133-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/Alembic-Migrations-6BA81E" alt="Alembic" />
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [License](#license)

---

## Overview

**Logistics System** is a backend API designed for managing logistics operations across multiple tenants. Each tenant operates in an isolated context, with their own users, shipments, and tracking data. The system supports full shipment lifecycle management — from creation to delivery — with role-based access control, JWT authentication, and real-time status tracking.

---

## Features

| Category | Details |
|---|---|
| **Multi-Tenancy** | Tenant isolation via slug-based headers (`X-Tenant-Slug`), soft-delete support |
| **Authentication** | JWT access tokens (HS256), secure refresh token rotation with SHA-256 hashing |
| **Role-Based Access** | `ADMIN`, `OPERATOR`, `VIEWER` roles per tenant |
| **Shipment Management** | Create shipments, assign drivers, auto-generated tracking numbers |
| **Shipment Tracking** | Real-time status tracking (`CREATED → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED`) |
| **Status Audit Log** | Full history of status changes with timestamps, location, and responsible user |
| **Soft Deletes** | Tenants support soft deletion with partial unique indexes |
| **Async I/O** | Fully asynchronous with `asyncpg` and SQLAlchemy 2.0 async sessions |
| **Database Migrations** | Versioned schema migrations via Alembic |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (async) |
| Database | [PostgreSQL](https://www.postgresql.org/) via `asyncpg` |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Auth | [python-jose](https://github.com/mpdavis/python-jose) (JWT) + [passlib](https://passlib.readthedocs.io/) (bcrypt) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |

---

## Project Structure

```
logistics_backend/
├── app/
│   ├── main.py                  # Application entry point & router registration
│   ├── core/
│   │   ├── config.py            # Environment settings (DATABASE_URL, SECRET_KEY)
│   │   ├── database.py          # Async engine, session factory, get_db dependency
│   │   ├── dependencies.py      # get_current_user & get_current_tenant guards
│   │   ├── security.py          # Password hashing, JWT creation & verification
│   │   ├── base.py              # TimeStampMixIn (created_at, updated_at, deleted_at)
│   │   └── utility.py           # Shared utility functions
│   ├── modules/
│   │   ├── tenants/             # Tenant CRUD (create, list, soft-delete)
│   │   │   ├── models.py
│   │   │   ├── schema.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── dependencies.py
│   │   ├── users/               # User registration & login
│   │   │   ├── models.py
│   │   │   ├── schema.py
│   │   │   ├── respository.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── dependencies.py
│   │   ├── auth/                # Token refresh & current user endpoints
│   │   │   ├── models.py
│   │   │   ├── schema.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── dependencies.py
│   │   └── shipments/           # Shipment creation & tracking
│   │       ├── models.py
│   │       ├── schema.py
│   │       ├── enum.py
│   │       ├── repository.py
│   │       ├── service.py
│   │       ├── router.py
│   │       └── dependencies.py
│   └── shared/
│       ├── enums.py
│       └── base_model.py
├── migrations/                  # Alembic migration versions
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker services definition
├── .env                         # Environment variables (not committed)
└── .gitignore
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+** (running locally or via Docker)
- **pip** or **virtualenv**

### 1. Clone the Repository

```bash
git clone https://github.com/DevSaadSaboor/Logistics_System.git
cd Logistics_System
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/logistics
SECRET_KEY=your-super-secret-key
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**. Interactive docs are at **http://localhost:8000/docs**.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Secret key for signing JWT tokens | `my-very-secret-key-change-me` |

---

## Database Migrations

This project uses **Alembic** for versioned database migrations.

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Rollback one step
alembic downgrade -1
```

---

## API Reference

### Health Check

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Returns `{"message": "Backend is running"}` |

### Tenants

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tenants/` | Create a new tenant |
| `GET` | `/tenants/` | List all tenants |
| `DELETE` | `/tenants/{tenant_id}` | Soft-delete a tenant |

### Users / Auth

| Method | Endpoint | Headers | Description |
|---|---|---|---|
| `POST` | `/auth/register` | `X-Tenant-Slug` | Register a new user under a tenant |
| `POST` | `/auth/login` | `X-Tenant-Slug` | Login and receive JWT + refresh token |
| `GET` | `/auth/me` | `Authorization: Bearer <token>` | Get current authenticated user |
| `POST` | `/auth/refresh` | `X-Tenant-Slug` | Refresh an expired access token |

### Shipments

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/shipments/` | Bearer + `X-Tenant-Slug` | Create a new shipment |
| `GET` | `/shipments/shipments/track/{tracking_number}` | — | Track a shipment by tracking number |

---

## Authentication

The API uses a **JWT + Refresh Token** strategy:

1. **Register** a user under a tenant via `POST /auth/register` with the `X-Tenant-Slug` header.
2. **Login** via `POST /auth/login` to receive an `access_token` and `refresh_token`.
3. **Access protected endpoints** by passing the access token in the `Authorization: Bearer <token>` header.
4. **Refresh** expired access tokens via `POST /auth/refresh` using the refresh token.

### Token Details

| Token | Lifetime | Storage |
|---|---|---|
| Access Token | 60 minutes | Client-side (memory / httpOnly cookie) |
| Refresh Token | 7 days | Hashed (SHA-256) in `refresh_tokens` table |

### User Roles

| Role | Description |
|---|---|
| `ADMIN` | Full system access |
| `OPERATOR` | Operational access (shipments, tracking) |
| `VIEWER` | Read-only access |

---

## License

This project is for educational and portfolio purposes. Feel free to fork and adapt it to your needs.

---

<p align="center">
  Built with ❤️ using <strong>FastAPI</strong> &amp; <strong>PostgreSQL</strong>
</p>
