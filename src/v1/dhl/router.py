from fastapi import APIRouter, Depends, Query
from src.v1.dhl import service as DhlService
from src.v1.dhl import schemas as DhlSchemas
from src.v1.dhl import utils as DhlUtils
from src.v1.dhl import models as DhlModels
from typing import Dict, Any
from src.database import get_db

router = APIRouter(prefix="/dhl", tags=["dhl"])


@router.post("/create-shipment", response_model=Dict[str, Any], status_code=201)
async def create_shipment(shipment_data: DhlSchemas.ShipmentData):
    shipment = await DhlService.create_dhl_shipment(shipment_data.dict())

    return shipment


@router.post("/create-warehouse-shipment", status_code=201)
async def create_warehouse_shipment(
    supplier_order_id: int,
    pickup_date: str,
    db=Depends(get_db),
):
    shipment_data = DhlUtils.collect_shipment_info(pickup_date, supplier_order_id, db)
    shipment = await DhlService.create_dhl_shipment(shipment_data)

    warehouse_shipment = DhlModels.DbDhlWarehouseShipment(
        proforma_invoice_number=shipment_data["invoiceNumber"],
        supplier_order_id=supplier_order_id,
        pickup_date=pickup_date,
        name=shipment_data["name"],
        address1=shipment_data["address1"],
        address2=shipment_data["address2"],
        city=shipment_data["City"],
        state_or_region=shipment_data["StateOrRegion"],
        postal_code=shipment_data["PostalCode"],
        country_code=shipment_data["CountryCode"],
        phone=shipment_data["Phone"],
        quantity=shipment_data["totalQuantityOrdered"],
        total_items_price=shipment_data["totalItemsPrice"],
        net_weight=shipment_data["netWeight"],
        gross_weight=shipment_data["grossWeight"],
        status=shipment["status"],
        filepath=shipment["filepath"],
        tracking_number=shipment["shipmentTrackingNumber"],
        tracking_url=shipment["trackingUrl"],
    )

    db.add(warehouse_shipment)
    db.commit()

    result = {
        "status": "success",
        "message": "Warehouse shipment created successfully",
        "proforma_invoice_number": shipment_data["invoiceNumber"],
        "supplier_order_id": supplier_order_id,
        "filepath": shipment["filepath"],
        "tracking_number": shipment["shipmentTrackingNumber"],
        "tracking_url": shipment["trackingUrl"],
    }

    return result
