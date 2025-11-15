from ninja import Router, PatchDict, UploadedFile, File
from django.contrib.auth import get_user_model
from .schema import *
from user.schema import Message
from typing import *
from .models import *
from django.core.cache import cache
from django.db import transaction
from .utils.pdf_generator import InvoicePDFGenerator

User = get_user_model()
order_api = Router(tags=["Order"])

@transaction.atomic
@order_api.post("/create-order", response={201: Message, 401: Message, 404: Message})
def create_order(request, data: OrderCreation):
    user = request.auth
    if not Company.objects.filter(user=user).exists():
        return 404, {"message": "Company not found"}
    company = Company.objects.get(user=user)
    order = Order.objects.filter(company=company).last()
    customer = Parties.objects.get(id=data.customer_id)
    is_sale = data.sale_type
    invoice_number = order.id + 1 if order else 1
    invoice_number = f"{'inv' if data.sale_type else 'pinv'}-{invoice_number}"
    order = Order.objects.create(company=company, is_sale=is_sale, customer=customer, invoice_number=invoice_number, vehicle_number = data.vehicle_number)
    total_amount = 0.0
    for item in data.order_items:
        item_product = Product.objects.get(id=item.item_id)
        OrderItem.objects.create(
            order=order,
            product=item_product,
            quantity=item.quantity,
            price=item_product.price,
        )
        total_amount += float(item_product.price) * float(item.quantity)
    order.transport_charges = data.transport_charges
    order.include_tc_gst = data.include_tc_gst
    order.total_amount = total_amount 
    order.gst_amount = data.gst_percentage
    order.save()
    return 201, {"message": "Order created successfully"}

@order_api.get("/get-sale", response={200: List[OrderSchema], 404: Message})
def get_sale(request):
    user = request.auth
    sales = Order.objects.filter(company__user=user, is_sale=True).select_related("customer").order_by('-id')
    data = []
    for sale in sales:
        data.append({
            "id": sale.id,
            "customer": sale.customer.name,
            "invoice_number": sale.invoice_number,
            "total_amount": sale.total_amount,
            "order_date": sale.order_date.strftime("%Y-%m-%d"),
        })
    return 200, data

@order_api.get("/get-purchase", response={200: List[OrderSchema], 404: Message})
def get_purchase(request):
    user = request.auth
    purchase = Order.objects.filter(company__user=user, is_sale=False).select_related("customer").order_by('-id')
    data = []
    for purch in purchase:
        data.append({
            "id": purch.id,
            "customer": purch.customer.name,
            "invoice_number": purch.invoice_number,
            "total_amount": purch.total_amount,
            "order_date": purch.order_date.strftime("%Y-%m-%d"),
        })
    return 200, data

@order_api.get("/get-items", response={200: List[OrderItemSchema], 404: Message})
def get_items(request, id: int):
    user = request.auth
    order = Order.objects.get(company__user=user, id=id)
    items = OrderItem.objects.filter(order=order)
    return 200, list(items)

@order_api.patch("/update-order", response={200: OrderSchema, 404: Message})
def update_order(request, data: PatchDict[OrderSchema]):
    user = request.auth
    if not Order.objects.filter(company__user=user, id=data['id']).exists():
        return 404, {"message": "Order not found"}
    order = Order.objects.get(company__user=user, id=data['id'])
    if 'customer_id' in data:
        if not Parties.objects.get(id=data['customer_id']).exists():
            return 400, {"message": "Customer not found"}
        Parties.objects.get(id=data['customer_id'])
    if 'product_id' in data:
        if not Product.objects.get(id=data['product_id']).exists():
            return 400, {"message": "Product not found"}
        Product.objects.get(id=data['product_id'])
    if 'total_amount' in data:
        order.total_amount = data['total_amount']
    if 'sale_type' in data:
        order.is_sale = data['sale_type']
        prefix = 'inv' if data['sale_type'] else 'pinv'
        order.order_number = f"{prefix}-{order.invoice_number:06d}"
    if 'order_items' in data:
        OrderItem.objects.filter(order=order).delete()
        for item_data in data['order_items']:
            try:
                item_product = Product.objects.get(id=item_data['id'])
                OrderItem.objects.create(
                    order=order,
                    product=item_product,
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                    total_price=item_data['total_price']
                )
            except Product.DoesNotExist:
                return 400, {"message": f"Product with id {item_data['id']} not found"}
    order.save()
    return 200, order

@order_api.delete("/delete-order", response={200: Message, 404: Message})
def delete_order(request, id: int):
    user = request.auth
    Order.objects.filter(company__user=user, id=id).delete()
    return 200, {"message": "Order deleted succesfully "}

@order_api.get("/invoice-pdf/{order_id}")
def get_invoice_pdf(request, order_id: int):
    user = request.auth
    try:
        order = Order.objects.select_related('customer', 'company').prefetch_related('items__product').get(id=order_id, company__user=user)
    except Order.DoesNotExist:
        return 404, {"message": "Order not found"}
    pdf_generator = InvoicePDFGenerator(order)
    return pdf_generator.get_http_response()