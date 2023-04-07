from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Numeric
from src.database import Base
from sqlalchemy import Column


class DbSupplierOrderItem(Base):
    __tablename__ = "supplier_order_item"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    sku = Column(String)
    asin = Column(String)
    fnsku = Column(String)
    product = Column(String)
    size = Column(String)
    quantity_ordered = Column(Integer)
    item_price_wo_vat = Column(Numeric(precision=10, scale=2))
    item_price_vat = Column(Numeric(precision=10, scale=2))
    total_price_wo_vat = Column(Numeric(precision=10, scale=2))
    total_price_vat = Column(Numeric(precision=10, scale=2))
