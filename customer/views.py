from ninja import Router, PatchDict, UploadedFile, File
from django.contrib.auth import get_user_model
from .schema import *
from user.schema import Message
from typing import *
from .models import *
from django.core.cache import cache

User = get_user_model()
customer_api = Router(tags=["Customer"])

@customer_api.post("/create-customer", response={201: Message, 401: Message, 404: Message})
def create_customer(request, data: CustomerCreation):
    user = request.auth
    company = Company.objects.get(user=user)
    if Parties.objects.filter(gst_number=data.gst_number, company=company).exists():
        return 401, {"message": "Customer with this GST number already exists"}
    Parties.objects.create(company=company, **data.dict())
    return 201, {"message": "Customer created successfully"}

@customer_api.get("/get-customer", response={200: List[CustomerSchema], 404: Message})
def get_customer(request):
    user = request.auth
    return 200, list(Parties.objects.filter(company__user=user, is_vendor=False).only('id', 'name', 'gst_number', 'phone_number'))

@customer_api.get("/get-vendor", response={200: List[CustomerSchema], 404: Message})
def get_vendor(request):
    user = request.auth
    return 200, list(Parties.objects.filter(company__user=user, is_vendor=True))

@customer_api.patch("/update-customer", response={200: CustomerSchema, 404: Message})
def update_customer(request, data: PatchDict[CustomerSchema]):
    user = request.auth
    if not Parties.objects.filter(company__user=user, id=data['id']).exists():
        return 404, {"message": "Customer not found"}
    customer = Parties.objects.get(company__user=user, id=data['id'])
    for attr, value in data.items():
        setattr(customer, attr, value)
    customer.save()
    return 200, customer

@customer_api.delete("/delete-customer", response={200: Message, 404: Message})
def delete_customer(request, id: int):
    user = request.auth
    Parties.objects.filter(company__user=user, id=id).delete()
    return 200, {"message": "Customer deleted succesfully "}