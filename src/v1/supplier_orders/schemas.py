from decimal import Decimal
from pydantic import BaseModel


class SupplierOrderItemBase(BaseModel):
    order_id: int
    sku: str
    asin: str
    fnsku: str
    product: str
    size: str
    quantity_ordered: int
    item_price_wo_vat: Decimal
    item_price_vat: Decimal
    total_price_wo_vat: Decimal
    total_price_vat: Decimal


class SupplierOrderItemDisplay(SupplierOrderItemBase):
    id: int

    class Config:
        orm_mode = True


class SupplierOrderItemUpdate(BaseModel):
    order_id: int = None
    sku: str = None
    asin: str = None
    fnsku: str = None
    product: str = None
    size: str = None
    quantity_ordered: int = None
    item_price_wo_vat: Decimal = None
    item_price_vat: Decimal = None
    total_price_wo_vat: Decimal = None
    total_price_vat: Decimal = None


class SupplierOrderItemDelete(BaseModel):
    id: int
