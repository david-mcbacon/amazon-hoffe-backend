import json
import base64
import datetime
from dotenv import load_dotenv
import os

from sqlalchemy import func

from src.v1.dhl import schemas as DhlSchemas
from src.database import get_db
from src.v1.supplier_orders import models as SupplierOrderModels
from src.v1.dhl import models as DhlModels
from src.v1.fba_shipment import models as FbaShipmentModels

load_dotenv(".env")

DHL_ACCOUNT_NUMBER = os.environ.get("DHL_ACCOUNT_NUMBER")

# ---------------------------- #
#       LOGO, SIGNATURE        #
# ---------------------------- #

with open(
    "./src/v1/dhl/img/hoffe-logo-black.png",
    "rb",
) as f:
    content = f.read()
    encoded_content = base64.b64encode(content).decode("utf-8")

with open(
    "./src/v1/dhl/img/ds-signature.png",
    "rb",
) as f:
    signature_image = base64.b64encode(f.read()).decode("utf-8")


def ship_tp_amazon_warehouse_payload(shipment_data: dict) -> json:
    shipment_request_data = {
        "getOptionalInformation": True,
        "productCode": "P",
        "plannedShippingDateAndTime": f"{shipment_data['pickupDate']}T10:00:00 GMT+01:00",
        "pickup": {
            "isRequested": True,
            "closeTime": "15:00",
            "location": "reception",
            "pickupDetails": {
                "postalAddress": {
                    "postalCode": "05201",
                    "cityName": "Spisska Nova Ves",
                    "countryCode": "SK",
                    "addressLine1": "Zimna 94",
                    "addressLine2": "budova Zdruzena",
                    "countryName": "Slovakia",
                },
                "contactInformation": {
                    "email": "info@hoffebelts.sk",
                    "phone": "+421918573607",
                    "mobilePhone": "+421918573607",
                    "companyName": "Peter Hoffelder",
                    "fullName": "Peter Hoffelder",
                },
            },
        },
        "accounts": [{"number": DHL_ACCOUNT_NUMBER, "typeCode": "shipper"}],
        "outputImageProperties": {
            "encodingFormat": "pdf",
            "imageOptions": [
                {"typeCode": "invoice", "invoiceType": "proforma", "isRequested": True},
                {
                    "typeCode": "label",
                    "templateName": "ECOM26_84_001",
                    "labelFreeText": "HoffeBelts Amazon order",
                },
                {
                    "typeCode": "waybillDoc",
                    "isRequested": True,
                    "hideAccountNumber": True,
                },
            ],
            "allDocumentsInOneImage": True,
            "splitDocumentsByPages": True,
            "customerLogos": [
                {
                    "fileFormat": "PNG",
                    "content": encoded_content,
                }
            ],
        },
        "customerDetails": {
            "shipperDetails": {
                "postalAddress": {
                    "cityName": "Spisska Nova Ves",
                    "countryCode": "SK",
                    "postalCode": "052 01",
                    "addressLine1": "J. Holleho 1035/17",
                },
                "contactInformation": {
                    "phone": "+421949022091",
                    "companyName": "Bacon Solutions, s.r.o.",
                    "fullName": "David Slaninka",
                    "email": "hoffebelts.amazon@gmail.com",
                },
                "registrationNumbers": [
                    {
                        "typeCode": "EOR",
                        "number": "SK2120897064",
                        "issuerCountryCode": "SK",
                    }
                ],
                "typeCode": "private",
            },
            "receiverDetails": {
                "postalAddress": {
                    "cityName": shipment_data["City"],
                    "countryCode": shipment_data["CountryCode"],
                    "postalCode": shipment_data["PostalCode"],
                    "addressLine1": shipment_data["address1"],
                    # "addressLine2": shipment_data["address2"],
                },
                "contactInformation": {
                    "phone": shipment_data["Phone"],
                    "companyName": shipment_data["name"],
                    "fullName": shipment_data["name"],
                },
                "typeCode": "private",
            },
        },
        "content": {
            "unitOfMeasurement": "metric",
            "isCustomsDeclarable": True,
            "incoterm": "DAP",
            "description": "Handmade leather belt",
            "packages": [
                {
                    "customerReferences": [
                        {"value": "HoffeBelts Amazon order", "typeCode": "CU"}
                    ],
                    "weight": shipment_data["grossWeight"],
                    "dimensions": {"length": 22, "width": 32, "height": 5},
                }
            ],
            "declaredValueCurrency": "USD",
            "declaredValue": shipment_data["totalItemsPrice"],
            "exportDeclaration": {
                "lineItems": [
                    {
                        "number": 1,
                        "description": "Belts and bandoliers with or without buckles - Articles of apparel and clothing accessories, of leather or of composition leather.",
                        "price": shipment_data["avgPrice"],
                        "priceCurrency": "USD",
                        "quantity": {
                            "value": shipment_data["totalQuantityOrdered"],
                            "unitOfMeasurement": "PCS",
                        },
                        "commodityCodes": [
                            {"typeCode": "inbound", "value": "4203.30.000"}
                        ],
                        "exportReasonType": "permanent",
                        "manufacturerCountry": "SK",
                        "weight": {
                            "netValue": shipment_data["netWeight"],
                            "grossValue": shipment_data["grossWeight"],
                        },
                    }
                ],
                "invoice": {
                    "number": shipment_data["invoiceNumber"],
                    "date": datetime.date.today().isoformat(),
                    "signatureName": "Slaninka",
                    "signatureTitle": "Mr.",
                    "signatureImage": signature_image,
                    "totalNetWeight": shipment_data["netWeight"],
                    "totalGrossWeight": shipment_data["grossWeight"],
                },
                # "additionalCharges": [
                #     {
                #         "value": shipment_data["totalShippingPrice"],
                #         "caption": "Shipping fee",
                #         "typeCode": "freight",
                #     }
                # ],
                "exportReason": "Commercial",
                "exportReasonType": "permanent",
                "placeOfIncoterm": "Spisska Nova Ves",
            },
        },
        "valueAddedServices": [{"serviceCode": "WY"}],
    }

    return json.dumps(shipment_request_data)


def collect_shipment_info(pickup_date: str, suppliper_order_id: int, db) -> dict:

    total_price_and_quantity = (
        db.query(SupplierOrderModels.DbSupplierOrderItem)
        .filter(SupplierOrderModels.DbSupplierOrderItem.order_id == suppliper_order_id)
        .with_entities(
            func.sum(SupplierOrderModels.DbSupplierOrderItem.total_price_wo_vat),
            func.sum(SupplierOrderModels.DbSupplierOrderItem.quantity_ordered),
        )
        .first()
    )

    last_proforma_number = db.query(
        func.max(DhlModels.DbDhlWarehouseShipment.proforma_invoice_number)
    ).scalar()

    total_price = float(total_price_and_quantity[0])
    quantity = total_price_and_quantity[1]

    fba_shipment_plan = (
        db.query(FbaShipmentModels.DbFbaShipmentPlan)
        .filter(
            FbaShipmentModels.DbFbaShipmentPlan.supplier_order_id == suppliper_order_id
        )
        .one()
    )

    name = f"Amazon warehouse {fba_shipment_plan.fulfillment_center_id}"

    shipment_data = {
        "invoiceNumber": str(int(last_proforma_number) + 1),
        "pickupDate": pickup_date,
        "name": name,
        "address1": fba_shipment_plan.address_line_1,
        "address2": "",
        "City": fba_shipment_plan.city,
        "StateOrRegion": fba_shipment_plan.state_or_province_code,
        "PostalCode": fba_shipment_plan.postal_code,
        "CountryCode": fba_shipment_plan.country_code,
        "Phone": "8664958567",
        "totalQuantityOrdered": quantity,
        "totalShippingPrice": 0,
        "avgPrice": round(total_price / float(quantity), 3),
        "netWeight": 8,
        "grossWeight": 8,
        "totalItemsPrice": total_price,
        "skuList": "",
        "totalDiscount": "",
    }
    return shipment_data
