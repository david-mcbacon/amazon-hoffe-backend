# How to create FBA shipment
1. Add order data to supplier_order_item table
2. Run /api/v1/fba-shipment/create, which will create shipment in amazon and fill fba_shipment_plan table
3. Go to seller central, switch to Send to FBA workflow, add box size, weight and create shipment. Edit name of shipment - add proforma number 
4. Run /api/v1/dhl/create-warehouse-shipment, which will create shipment in DHL and fill dhl_shipment table and create PDF label
