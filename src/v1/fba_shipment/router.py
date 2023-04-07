from fastapi import APIRouter, Depends, HTTPException, Response, status, Request

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.database import get_db

from src.v1.fba_shipment import service as FbaShipmentService
from src.v1.supplier_orders import models as SupplierOrderModels
from src.v1.fba_shipment import utils as FbaShipmentUtils
from src.v1.fba_shipment import models as FbaShipmentModels

router = APIRouter(prefix="/fba-shipment", tags=["fba-shipment"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_fba_shipment(order_id: int, db: Session = Depends(get_db)):

    # 1. Get all supplier order items for the order
    supplier_order_items = db.query(SupplierOrderModels.DbSupplierOrderItem)
    if order_id:
        supplier_order_items = supplier_order_items.filter(
            SupplierOrderModels.DbSupplierOrderItem.order_id == order_id
        )

    supplier_order_items = supplier_order_items.all()
    sku_list = [item.sku for item in supplier_order_items]

    # 2. Get preparation instrucions
    prep_instructions = FbaShipmentService.get_prep_instructions(sku_list)

    # 3. Transform supplier order items to Amazon format
    shipment_plan_data = FbaShipmentUtils.transform_to_amazon_shipment_plan_format(
        supplier_order_items, prep_instructions
    )
    shipment_data = FbaShipmentUtils.transform_to_amazon_shipment_format(
        supplier_order_items
    )

    # 4. Create FBA shipment plan for the order
    fba_shipment_plan = FbaShipmentService.create_fba_shipment_plan(shipment_plan_data)

    # 5. Create FBA shipment for the order
    warehouse_code = fba_shipment_plan["DestinationFulfillmentCenterId"]
    shipment_id = fba_shipment_plan["ShipmentId"]

    fba_shipment = FbaShipmentService.create_fba_shipment(
        shipment_id=shipment_id,
        warehouse_code=warehouse_code,
        shipment_name=f"{order_id}-{warehouse_code}",
        shipment_items=shipment_data,
    )

    fba_shipment_id = fba_shipment.payload["ShipmentId"]

    if fba_shipment_id == shipment_id:
        shipment_plan_db_data = (
            FbaShipmentUtils.transform_shipment_plan_response_to_db_model(
                fba_shipment_plan, order_id
            )
        )
        db.add(shipment_plan_db_data)
        db.commit()
        db.refresh(shipment_plan_db_data)

        return shipment_plan_db_data

    else:
        return {
            "status": "error",
            "message": "Shipment plan and shipment are not matching.",
        }


@router.get("/get-labels")
async def get_fba_shipment_labels(
    shipment_id: str, ship_date: str, proforma_number: str
):
    # DHL shipment should be created first to get ship date and proforma number

    # 6. Get labels for the shipment
    # labels = FbaShipmentService.get_fba_shipment_labels(fba_shipment.payload["ShipmentId"])
    labels = FbaShipmentService.get_fba_shipment_labels(shipment_id)

    download_url = labels.payload["DownloadURL"]
    filename = f"files/dhl/AMZN_FBA_{ship_date}_{proforma_number}.pdf"

    file_download = await FbaShipmentUtils.download_pdf_from_url(download_url, filename)
    result = {
        "status": "success",
        "message": "File downloaded successfully.",
        "filepath": filename,
    }

    return result

    # 7. Update transport info
    # This is not working, CarrierName DHL is not supported.
    # transport = FbaShipmentService.update_fba_transport_info("FBA173F88VBT", 9945089486)
