from fastapi import FastAPI
from app.core.database import engine, Base
from app.modules.AI.vector_store import ensure_vector_store_initialized
from app.modules.tenants.router import router as tenant_router
from app.modules.users.router import router as auth_router
from app.modules.auth.router import router as current_user
from app.modules.shipments.router import router as shipment_router
from app.modules.AI.router import router as ai_router


app = FastAPI()


app.include_router(tenant_router)
app.include_router(auth_router)
app.include_router(current_user)
app.include_router(shipment_router)
app.include_router(ai_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    ensure_vector_store_initialized()


@app.get("/")
async def root():
    return {"message": "Backend is running"}

