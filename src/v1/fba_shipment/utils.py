import json
import aiohttp

from src.v1.fba_shipment import models as FbaShipmentModels


async def download_pdf_from_url(url: str, filename: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filename, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)


def transform_to_amazon_shipment_plan_format(
    supplier_order_items: list, prep_instructions: list
) -> list:
    transformed_data = []

    # prep_details_list = [
    #     {"PrepInstruction": "Polybagging", "PrepOwner": "SELLER"},
    #     {"PrepInstruction": "Labeling", "PrepOwner": "SELLER"},
    # ]

    for item in supplier_order_items:

        # find item sku in prep instructions and get PrepInstructionList
        for prep_instruction in prep_instructions:
            if prep_instruction["sku"] == item.sku:

                # prep_details_list = prep_instruction.prep_details_list
                prep_details_list = []
                for prep_detail in prep_instruction["PrepInstructionList"]:
                    prep_details_list.append(
                        {
                            "PrepInstruction": prep_detail,
                            "PrepOwner": "SELLER",
                        }
                    )
                break

        amazon_item = {
            "SellerSKU": item.sku,
            "ASIN": item.asin,
            "Condition": "NewItem",
            "Quantity": item.quantity_ordered,
            "QuantityInCase": 1,
            "PrepDetailsList": prep_details_list,
        }
        transformed_data.append(amazon_item)

    # print(json.dumps(transformed_data))
    return transformed_data


def transform_to_amazon_shipment_format(supplier_order_items: list) -> list:
    transformed_data = []

    # prep_details_list = [
    #     {"PrepInstruction": "Polybagging", "PrepOwner": "SELLER"},
    #     {"PrepInstruction": "Labeling", "PrepOwner": "SELLER"},
    # ]

    for item in supplier_order_items:
        amazon_item = {
            "SellerSKU": item.sku,
            "FulfillmentNetworkSKU": item.fnsku,
            "QuantityShipped": item.quantity_ordered,
            "QuantityInCase": 1,
            # "PrepDetailsList": prep_details_list,
        }
        transformed_data.append(amazon_item)

    # print(json.dumps(transformed_data))
    return transformed_data


def transform_shipment_plan_response_to_db_model(fba_shipment_plan, order_id):

    db_model = FbaShipmentModels.DbFbaShipmentPlan(
        supplier_order_id=order_id,
        shipment_id=fba_shipment_plan["ShipmentId"],
        fulfillment_center_id=fba_shipment_plan["DestinationFulfillmentCenterId"],
        name=fba_shipment_plan["ShipToAddress"]["Name"],
        address_line_1=fba_shipment_plan["ShipToAddress"]["AddressLine1"],
        city=fba_shipment_plan["ShipToAddress"]["City"],
        state_or_province_code=fba_shipment_plan["ShipToAddress"][
            "StateOrProvinceCode"
        ],
        country_code=fba_shipment_plan["ShipToAddress"]["CountryCode"],
        postal_code=fba_shipment_plan["ShipToAddress"]["PostalCode"],
        label_prep_type=fba_shipment_plan["LabelPrepType"],
        total_units=fba_shipment_plan["EstimatedBoxContentsFee"]["TotalUnits"],
        fee_currency_code=fba_shipment_plan["EstimatedBoxContentsFee"]["FeePerUnit"][
            "CurrencyCode"
        ],
        fee_per_unit_value=fba_shipment_plan["EstimatedBoxContentsFee"]["FeePerUnit"][
            "Value"
        ],
        total_fee_currency_code=fba_shipment_plan["EstimatedBoxContentsFee"][
            "TotalFee"
        ]["CurrencyCode"],
        total_fee_value=fba_shipment_plan["EstimatedBoxContentsFee"]["TotalFee"][
            "Value"
        ],
    )

    return db_model
