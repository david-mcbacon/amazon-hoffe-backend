from fastapi import APIRouter

from src.v1.dhl import router as dhl_router
from src.v1.supplier_orders import router as supplier_orders_router
from src.v1.fba_shipment import router as fba_shipment_router

router = APIRouter(prefix="/api/v1")

router.include_router(dhl_router.router)
router.include_router(supplier_orders_router.router)
router.include_router(fba_shipment_router.router)
