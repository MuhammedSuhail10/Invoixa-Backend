from ninja import Schema, ModelSchema
from typing import *

class CustomerCreation(Schema):
    name: str
    gst_number: str
    company_name: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: Optional[str] = "India"
    shipping_address_line_1: Optional[str] = None
    shipping_address_line_2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_pincode: Optional[str] = None
    shipping_country: Optional[str] = "India"
    phone_number: str
    email: str
    is_vendor: bool = False

class CustomerSchema(Schema):
    id: int
    name: str
    gst_number: str
    phone_number: str

class CustomerListSchema(Schema):
    id: int
    name: str