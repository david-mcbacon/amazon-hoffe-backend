from sqlalchemy import Column, Integer, String, Float
from src.database import Base


class DbDhlWarehouseShipment(Base):
    __tablename__ = "dhl_warehouse_shipment"

    id = Column(Integer, primary_key=True)
    proforma_invoice_number = Column(String)
    supplier_order_id = Column(Integer)
    pickup_date = Column(String)
    name = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state_or_region = Column(String)
    postal_code = Column(String)
    country_code = Column(String)
    phone = Column(String)
    quantity = Column(Integer)
    total_items_price = Column(Float)
    net_weight = Column(Float)
    gross_weight = Column(Float)
    #
    status = Column(String)
    filepath = Column(String)
    tracking_number = Column(String)
    tracking_url = Column(String)
