from ninja import Schema, ModelSchema
from typing import *

class ProductCreation(Schema):
    name: str
    hsn_code: str
    unit: str
    price: float

class ProductSchema(Schema):
    id: int
    name: str
    hsn_code: str