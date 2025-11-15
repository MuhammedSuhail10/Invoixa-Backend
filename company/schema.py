from ninja import Schema, ModelSchema
from typing import *
from .models import Company

class CompanyCreateSchema(Schema):
    name: str
    address: str
    phone_number: str
    email: str
    gst_number: str
    purchase_tax_percentage: float
    sales_tax_percentage: float

class CompanySchema(Schema):
    id: int
    user_id: int
    logo: str
    signature: str
    name: str
    address: str
    phone_number: str
    email: str
    gst_number: str
    purchase_tax_percentage: float
    sales_tax_percentage: float

class CompanyBankCreation(Schema):
    bank_name: str
    account_number: str
    ifsc_code: str
    branch_name: Optional[str] = None
    account_type: str
    upi_qr_code: Optional[str] = None

class CompanyBank(Schema):
    id: int
    company_id: int
    bank_name: str
    account_number: str
    ifsc_code: str
    branch_name: str
    account_type: str
    upi_qr_code: str