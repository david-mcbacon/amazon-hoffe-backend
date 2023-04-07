from fastapi import APIRouter, HTTPException, Depends
from typing import List

from . import schemas, models
from src.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/supplier_orders", tags=["supplier_orders"])


@router.get("/", response_model=List[schemas.SupplierOrderItemDisplay])
def get_all_supplier_orders(order_id: int = None, db: Session = Depends(get_db)):
    supplier_orders = db.query(models.DbSupplierOrderItem)
    if order_id:
        supplier_orders = supplier_orders.filter(
            models.DbSupplierOrderItem.order_id == order_id
        )
    return supplier_orders.all()


@router.get("/{id}", response_model=schemas.SupplierOrderItemDisplay)
def get_supplier_order(id: int, db: Session = Depends(get_db)):
    supplier_order = db.query(models.DbSupplierOrderItem).get(id)
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Supplier order not found")
    return supplier_order


@router.post("/", response_model=schemas.SupplierOrderItemDisplay)
def create_supplier_order(
    supplier_order: schemas.SupplierOrderItemBase, db: Session = Depends(get_db)
):
    new_supplier_order = models.DbSupplierOrderItem(**supplier_order.dict())
    db.add(new_supplier_order)
    db.commit()
    db.refresh(new_supplier_order)
    return new_supplier_order


@router.post("/bulk", response_model=List[schemas.SupplierOrderItemDisplay])
def create_supplier_orders(
    supplier_orders: List[schemas.SupplierOrderItemBase], db: Session = Depends(get_db)
):
    new_supplier_orders = [
        models.DbSupplierOrderItem(**supplier_order.dict())
        for supplier_order in supplier_orders
    ]
    db.bulk_save_objects(new_supplier_orders)
    db.commit()
    return new_supplier_orders


@router.put("/{id}", response_model=schemas.SupplierOrderItemDisplay)
def update_supplier_order(
    id: int,
    supplier_order: schemas.SupplierOrderItemUpdate,
    db: Session = Depends(get_db),
):
    existing_supplier_order = db.query(models.DbSupplierOrderItem).get(id)
    if not existing_supplier_order:
        raise HTTPException(status_code=404, detail="Supplier order not found")

    for attr, value in supplier_order.dict(exclude_unset=True).items():
        setattr(existing_supplier_order, attr, value)

    db.commit()
    db.refresh(existing_supplier_order)
    return existing_supplier_order


@router.put("/bulk", response_model=List[schemas.SupplierOrderItemDisplay])
def update_supplier_orders(
    supplier_orders: List[schemas.SupplierOrderItemUpdate],
    db: Session = Depends(get_db),
):
    for supplier_order in supplier_orders:
        existing_supplier_order = db.query(models.DbSupplierOrderItem).get(
            supplier_order.id
        )
        if not existing_supplier_order:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier order with id {supplier_order.id} not found",
            )

        for attr, value in supplier_order.dict(exclude_unset=True).items():
            setattr(existing_supplier_order, attr, value)

    db.commit()
    return supplier_orders


@router.delete("/{id}", response_model=schemas.SupplierOrderItemDelete)
def delete_supplier_order(id: int, db: Session = Depends(get_db)):
    supplier_order = db.query(models.DbSupplierOrderItem).get(id)
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Supplier order not found")

    db.delete(supplier_order)
    db.commit()
    return {"id": id}
