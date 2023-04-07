from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

from src.v1 import router as api_v1_router
from src.config import app_configs, settings
from src.database import Base, engine

from src.v1.supplier_orders import models  # imported only for creating tables
from src.v1.fba_shipment import models  # imported only for creating tables
from src.v1.dhl import models  # imported only for creating tables

app = FastAPI(**app_configs)
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(api_v1_router.router)

with engine.begin() as db:
    print("ℹ️  Database connected")
    Base.metadata.create_all(db)


@app.get("/")
def main():
    return {"data": "Hello"}


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
