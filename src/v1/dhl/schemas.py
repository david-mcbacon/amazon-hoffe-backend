from pydantic import BaseModel


class ShipmentData(BaseModel):
    invoiceNumber: str
    pickupDate: str
    name: str
    address1: str
    address2: str
    City: str
    StateOrRegion: str
    PostalCode: str
    CountryCode: str
    Phone: str
    totalQuantityOrdered: int
    totalShippingPrice: float
    avgPrice: float
    netWeight: float
    grossWeight: float
    totalItemsPrice: float
    skuList: str
    totalDiscount: str

    class Config:
        schema_extra = {
            "example": {
                "invoiceNumber": "20232001",
                "pickupDate": "2023-04-05",
                "name": "Amazon Warehouse FTW1",
                "address1": "33333 Lyndon B Johnson Freeway",
                "address2": "",
                "City": "Dallas",
                "StateOrRegion": "Texas",
                "PostalCode": "75241",
                "CountryCode": "US",
                "Phone": "8664958567",
                "totalQuantityOrdered": 27,
                "totalShippingPrice": 0,
                "avgPrice": 23.618,
                "netWeight": 8,
                "grossWeight": 8,
                "totalItemsPrice": 637.70,
                "skuList": "",
                "totalDiscount": "",
            }
        }


class WarehouseShipmentData(BaseModel):
    # ProformaInvoiceNumber: str
    # SupplierOrderId: int
    pickupDate: str
    # name: str
    # address1: str
    # address2: str
    # City: str
    # StateOrRegion: str
    # PostalCode: str
    # CountryCode: str
    # Phone: str
    # quantity: int
    # totalItemsPrice: float
    # netWeight: float
    # grossWeight: float

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "ProformaInvoiceNumber": "20232001",
    #             "SupplierOrderId": "202301",
    #             "pickupDate": "2023-04-05",
    #             "name": "Amazon Warehouse FTW1",
    #             "address1": "33333 Lyndon B Johnson Freeway",
    #             "address2": "",
    #             "City": "Dallas",
    #             "StateOrRegion": "Texas",
    #             "PostalCode": "75241",
    #             "CountryCode": "US",
    #             "Phone": "8664958567",
    #             "quantity": 27,
    #             "totalItemsPrice": 637.70,
    #             "netWeight": 8,
    #             "grossWeight": 8,
    #         }
    #     }
