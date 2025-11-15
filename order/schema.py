from ninja import Schema, ModelSchema
from typing import *

class OrderItemCreate(Schema):
    item_id: int
    quantity: int

class OrderCreation(Schema):
    customer_id: int
    sale_type: bool
    include_tc_gst: bool
    transport_charges: float
    gst_percentage: Optional[float] = 18.0
    vehicle_number: Optional[str] = None
    order_items: List[OrderItemCreate]

class OrderSchema(Schema):
    id: int
    customer: str
    invoice_number: str
    total_amount: float
    order_date: str

class OrderItemSchema(Schema):
    id: int
    quantity: int
    price: float
    total_price: float