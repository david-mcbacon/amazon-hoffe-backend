from sqlalchemy import Column, Integer, String, Float
from src.database import Base


class DbFbaShipmentPlan(Base):
    __tablename__ = "fba_shipment_plan"

    id = Column(Integer, primary_key=True)
    supplier_order_id = Column(Integer)
    shipment_id = Column(String)
    fulfillment_center_id = Column(String)
    name = Column(String)
    address_line_1 = Column(String)
    city = Column(String)
    state_or_province_code = Column(String)
    country_code = Column(String)
    postal_code = Column(String)
    label_prep_type = Column(String)
    total_units = Column(Integer)
    fee_currency_code = Column(String)
    fee_per_unit_value = Column(Float)
    total_fee_currency_code = Column(String)
    total_fee_value = Column(Float)
