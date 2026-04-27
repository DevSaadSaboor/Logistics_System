from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.database import engine, Base
from app.modules.AI.vector_store import ensure_vector_store_initialized
from app.modules.tenants.router import router as tenant_router
from app.modules.users.router import router as auth_router
from app.modules.auth.router import router as current_user
from app.modules.shipments.router import router as shipment_router
from app.modules.AI.router import router as ai_router

from app.core.exceptions import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    TenantNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    ShipmentNotFoundError,
    InvalidStatusTransitionError,
)

from app.core.logging import logger

app = FastAPI()


# ---------- Global Exception Handlers ----------
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.exception_handler(ShipmentNotFoundError)
async def shipment_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Shipment not found"
        }
    )


@app.exception_handler(InvalidStatusTransitionError)
async def invalid_status_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": str(exc)
        }
    )
@app.exception_handler(TenantNotFoundError)
async def tenant_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Tenant not found"}
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": "User already exists"}
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"success": False, "error": "Unauthorized: invalid credentials"}
    )


# ---------- Routers ----------
app.include_router(tenant_router)
app.include_router(auth_router)
app.include_router(current_user)
app.include_router(shipment_router)
app.include_router(ai_router)


# ---------- Startup ----------
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    ensure_vector_store_initialized()
    logger.info("Application started successfully")


# ---------- Root ----------
@app.get("/")
async def root():
    return {"message": "Backend is running"}