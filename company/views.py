from ninja import Router, PatchDict, UploadedFile, File
from django.contrib.auth import get_user_model
from .schema import *
from user.schema import Message
from typing import *
from .models import *
from django.core.cache import cache

User = get_user_model()
company_api = Router(tags=["Company"])

@company_api.post("/create-company", response={201: Message, 401: Message, 404: Message})
def create_company(request, data: CompanyCreateSchema, logo: UploadedFile = File(None), signature: UploadedFile = File(None)):
    user = request.auth
    if Company.objects.filter(user=user).exists():
        return 401, {"message": "Company already exists"}
    if Company.objects.filter(gst_number=data.gst_number).exists():
        return 401, {"message": "Company with this GST number already exists"}
    company = Company.objects.create(
        user=user,
        logo=logo,
        signature=signature,
        **data.dict()
    )   
    return 201, {"message": "Company created successfully"}

@company_api.get("/get-company", response={200: CompanySchema, 404: Message})
def get_company(request):
    user = request.auth
    if Company.objects.filter(user=user).exists():
        company = Company.objects.get(user=user)
        return 200, company
    return 404, {"message": "Company not found"}

@company_api.patch("/update-company", response={200: CompanySchema, 404: Message})
def update_company(request, data: PatchDict[CompanySchema]):
    user = request.auth
    if not Company.objects.filter(user=user).exists():
        return 404, {"message": "Company not found"}
    company = Company.objects.get(user=user)
    for attr, value in data.items():
        setattr(company, attr, value)
    company.save()
    return 200, company

@company_api.post("/change-signature", response={200: CompanySchema, 404: Message})
def change_signature(request, signature: UploadedFile = File(...)):
    user = request.auth
    if not Company.objects.filter(user=user).exists():
        return 404, {"message": "Company not found"}
    company = Company.objects.get(user=user)
    company.signature = signature
    company.save()
    return 200, company

@company_api.post("/create-bank-details", response={201: Message, 401: Message, 404: Message})
def create_bank(request, data: CompanyBankCreation):
    user = request.auth
    company = Company.objects.get(user=user)
    CompanyBankDetail.objects.create(company=company, **data.dict())
    return 201, {"message": "Bank details added succesfully"}

@company_api.get("/get-bank-details", response={200: List[CompanyBank], 404: Message})
def get_bank(request):
    user = request.auth
    company_bank = CompanyBankDetail.objects.filter(company__user=user)
    return 200, list(company_bank)

@company_api.patch("/update-bank-details", response={200: CompanyBank, 404: Message})
def update_bank(request, data: PatchDict[CompanyBank]):
    user = request.auth
    if not CompanyBank.objects.filter(user=user).exists():
        return 404, {"message": "Bank details not found"}
    company = CompanyBank.objects.get(user=user)
    for attr, value in data.items():
        setattr(company, attr, value)
    company.save()
    return 200, company

@company_api.delete("/delete-bank-details", response={200: Message, 404: Message})
def delete_bank(request, id: int):
    user = request.auth
    CompanyBank.objects.filter(user=user, id=id).delete()
    return 200, {"message": "Bank details deleted succesfully"}