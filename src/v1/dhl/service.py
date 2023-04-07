import aiohttp
import asyncio
import json
import base64
from dotenv import load_dotenv
import os
from fastapi import HTTPException

from src.v1.dhl import utils as DhlUtils

load_dotenv(".env")

DHL_USERNAME = os.environ.get("DHL_USERNAME")
DHL_PASSWORD = os.environ.get("DHL_PASSWORD")
DHL_ACCOUNT_NUMBER = os.environ.get("DHL_ACCOUNT_NUMBER")
DHL_API_ENDPOINT_TEST = "https://express.api.dhl.com/mydhlapi/test/shipments"
DHL_API_ENDPOINT_PROD = "https://express.api.dhl.com/mydhlapi/shipments"

dhl_credentials = f"{DHL_USERNAME}:{DHL_PASSWORD}"
encoded_dhl_credentials = base64.b64encode(dhl_credentials.encode("utf-8")).decode(
    "utf-8"
)


async def create_dhl_shipment(shipment_data):
    request_data: json = DhlUtils.ship_tp_amazon_warehouse_payload(shipment_data)
    # print(request_data)
    pickup_date = shipment_data.get("pickupDate")
    invoice_number = shipment_data.get("invoiceNumber")

    headers = {
        "Authorization": f"Basic {encoded_dhl_credentials}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(DHL_API_ENDPOINT_TEST, data=request_data) as response:
            response_text = await response.text()

            # Save PDF from response to file
            if response.status == 201:
                response_dict = json.loads(response_text)
                # print(json.loads(response_text))
                if "documents" in response_dict and len(response_dict["documents"]) > 0:
                    document_content = response_dict["documents"][0]["content"]
                    pdf_bytes = base64.b64decode(document_content)
                    filepath = f"./files/dhl/DHL_FBA_{pickup_date}_{invoice_number}.pdf"
                    with open(filepath, "wb") as f:
                        f.write(pdf_bytes)
                        f.close()

                    result = {
                        "status": "success",
                        "filepath": filepath,
                        "shipmentTrackingNumber": response_dict[
                            "shipmentTrackingNumber"
                        ],
                        "trackingUrl": response_dict["trackingUrl"],
                        "shipmentDetails": response_dict["shipmentDetails"],
                    }

                    return result
                else:
                    # return http exception
                    return HTTPException(status_code=500, detail="No documents found")
            else:
                return HTTPException(status_code=500, detail=response_text)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_dhl_shipment())
