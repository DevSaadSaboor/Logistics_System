from fastapi import FastAPI
from app.core.database import engine, Base

# IMPORTANT: import models so SQLAlchemy sees them
from app.modules.tenants.models import Tenant  # noqa

app = FastAPI()

from app.modules.tenants.router import router as tenant_router
from app.modules.users.router import router as auth_router
from app.modules.auth.router import router as current_user

app.include_router(tenant_router)
app.include_router(auth_router)
app.include_router(current_user)

# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Backend is running"}

