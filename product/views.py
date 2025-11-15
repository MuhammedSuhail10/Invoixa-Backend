from ninja import Router, PatchDict, UploadedFile, File
from django.contrib.auth import get_user_model
from .schema import *
from user.schema import Message
from typing import *
from .models import *
from django.core.cache import cache

User = get_user_model()
product_api = Router(tags=["Product"])

@product_api.post("/create-product", response={201: Message, 401: Message, 404: Message})
def create_product(request, data: ProductCreation):
    user = request.auth
    if not Company.objects.filter(user=user).exists():
        return 404, {"message": "Company not found"}
    company = Company.objects.get(user=user)
    if Product.objects.filter(hsn_code=data.hsn_code, company=company).exists():
        return 401, {"message": "Product with this HSN Code already exists"}
    Product.objects.create(company=company, **data.dict())
    return 201, {"message": "Product created successfully"}

@product_api.get("/get-product", response={200: List[ProductSchema], 404: Message})
def get_product(request):
    user = request.auth
    products = Product.objects.filter(company__user=user).only('id', 'name', 'hsn_code').order_by('-id')
    return 200, list(products)

@product_api.patch("/update-product", response={200: ProductSchema, 404: Message})
def update_product(request, data: PatchDict[ProductSchema]):
    user = request.auth
    if not Product.objects.filter(company__user=user, id=data['id']).exists():
        return 404, {"message": "Product not found"}
    product = Product.objects.get(company__user=user, id=data['id'])
    for attr, value in data.items():
        setattr(product, attr, value)
    product.save()
    return 200, product

@product_api.delete("/delete-product", response={200: Message, 404: Message})
def delete_product(request, id: int):
    user = request.auth
    Product.objects.filter(company__user=user, id=id).delete()
    return 200, {"message": "Product deleted succesfully "}