from sp_api.base import Marketplaces
from sp_api.api import FulfillmentInbound, ListingsItems
from dotenv import load_dotenv
import os
import time

from src.v1.supplier_orders import models as SupplierOrderModels
from src.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from src.v1.fba_shipment import utils as FbaShipmentUtils

load_dotenv(".env")


def sp_api_credentials():
    credentials = dict(
        refresh_token=os.environ.get("SP_API_REFRESH_TOKEN"),
        lwa_app_id=os.environ.get("LWA_APP_ID"),
        lwa_client_secret=os.environ.get("LWA_CLIENT_SECRET"),
        aws_access_key=os.environ.get("SP_API_ACCESS_KEY"),
        aws_secret_key=os.environ.get("SP_API_SECRET_KEY"),
        role_arn=os.environ.get("SP_API_ROLE_ARN"),
    )

    return credentials


def get_closed_shipments():

    shipments = FulfillmentInbound(
        credentials=sp_api_credentials(), marketplace=Marketplaces.US
    ).get_shipments(
        QueryType="SHIPMENT",
        MarketplaceId="ATVPDKIKX0DER",
        # ShipmentStatusList=["CLOSED"],
        # LastUpdatedAfter="2022-10-01T00:00:00Z",
        ShipmentIdList=["FBA1715HZ13X"],
    )

    print(shipments)


def get_prep_instructions(sku_list: list):
    prep_instructions = []
    for sku in sku_list:
        print(f"ℹ️  Getting prep instructions for {sku}")
        prep_instruction = FulfillmentInbound(
            credentials=sp_api_credentials(), marketplace=Marketplaces.US
        ).prep_instruction({"ShipToCountryCode": "US", "SellerSKUList": sku})

        selected_prep_instruction = {
            "sku": prep_instruction.payload["SKUPrepInstructionsList"][0]["SellerSKU"],
            "asin": prep_instruction.payload["SKUPrepInstructionsList"][0]["ASIN"],
            "PrepInstructionList": prep_instruction.payload["SKUPrepInstructionsList"][
                0
            ]["PrepInstructionList"],
        }
        prep_instructions.append(selected_prep_instruction)
        time.sleep(0.5)

    # print(prep_instructions)
    return prep_instructions


def create_fba_shipment_plan(plan_shipment_items: list):
    print(f"ℹ️  Creating shipment plan")
    shipment_plan_data = {
        "ShipFromAddress": {
            "Name": "David Slaninka",
            "AddressLine1": "Markusovska cesta 1",
            "AddressLine2": "",
            "DistrictOrCounty": "Slovakia",
            "City": "Spisska Nova Ves",
            "StateOrProvinceCode": "Slovakia",
            "CountryCode": "SK",
            "PostalCode": "05201",
        },
        "LabelPrepPreference": "SELLER_LABEL",
        "ShipToCountryCode": "US",
        "InboundShipmentPlanRequestItems": plan_shipment_items,
        # "InboundShipmentPlanRequestItems": [
        #     {
        #         "SellerSKU": "indigo_xxl",
        #         "ASIN": "B09KH88Z6W",
        #         "Condition": "NewItem",
        #         "Quantity": 1,
        #         "QuantityInCase": 1,
        #         "PrepDetailsList": [
        #             {"PrepInstruction": "Polybagging", "PrepOwner": "SELLER"},
        #             {"PrepInstruction": "Labeling", "PrepOwner": "SELLER"},
        #         ],
        #     }
        # ],
    }

    res = FulfillmentInbound(
        credentials=sp_api_credentials(), marketplace=Marketplaces.US
    ).plans(shipment_plan_data)

    inbound_shipment_plan = res.payload["InboundShipmentPlans"][0]
    print(inbound_shipment_plan)
    return inbound_shipment_plan


# create_shipment_plan()


def create_fba_shipment(
    shipment_id: str, warehouse_code: str, shipment_name: str, shipment_items: list
):

    shipment_data = {
        "InboundShipmentHeader": {
            "ShipmentName": shipment_name,
            "ShipFromAddress": {
                "Name": "David Slaninka",
                "AddressLine1": "Markusovska cesta 1",
                "DistrictOrCounty": "Slovakia",
                "City": "Spisska Nova Ves",
                "StateOrProvinceCode": "Slovakia",
                "CountryCode": "SK",
                "PostalCode": "05201",
            },
            "DestinationFulfillmentCenterId": warehouse_code,
            "AreCasesRequired": True,
            "ShipmentStatus": "WORKING",
            "LabelPrepPreference": "SELLER_LABEL",
            "IntendedBoxContentsSource": "NONE",  # tu mozno potrebujeme zmenit na FEED, aby sme mohli poslat XML cartons
        },
        # "InboundShipmentItems": [
        #     {
        #         "ShipmentId": "FBA1737H1269",
        #         "SellerSKU": "Bruce_l",
        #         "FulfillmentNetworkSKU": "B01JAXBWTU",
        #         "QuantityShipped": 20,
        #         "QuantityInCase": 1,
        #         "PrepDetailsList": [
        #             {"PrepInstruction": "Polybagging", "PrepOwner": "SELLER"}
        #         ],
        #     }
        # ],
        "InboundShipmentItems": shipment_items,
        "MarketplaceId": "ATVPDKIKX0DER",
    }

    shipment = FulfillmentInbound(
        credentials=sp_api_credentials(), marketplace=Marketplaces.US
    ).create_shipment(shipment_id, shipment_data)

    print(shipment)
    return shipment


def get_fba_shipment_labels(shipment_id: str):
    additional_params = {
        "PageType": "PackageLabel_A4_4",
        "PageSize": 1,
        "LabelType": "BARCODE_2D",
    }

    labels = FulfillmentInbound(
        credentials=sp_api_credentials(), marketplace=Marketplaces.US
    ).get_labels(shipment_id, **additional_params)

    print(labels)
    return labels


def update_fba_transport_info(shipment_id: str, tracking_id: int):
    additional_params = {
        "IsPartnered": False,
        "ShipmentType": "SP",
        "TransportDetails": {
            "NonPartneredSmallParcelData": {
                "CarrierName": "UPS",
                "PackageList": [
                    {"TrackingId": tracking_id},
                ],
            }
        },
    }

    transport_info = FulfillmentInbound(
        credentials=sp_api_credentials(), marketplace=Marketplaces.US
    ).update_transport_information(shipment_id, **additional_params)

    return transport_info
