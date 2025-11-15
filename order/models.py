from django.db import models
from company.models import Company
from customer.models import Parties
from product.models import Product

class Order(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='order_company')
    customer = models.ForeignKey(Parties, on_delete=models.CASCADE, related_name='order_customers')
    invoice_number = models.TextField(default="INV-1")
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    transport_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    include_tc_gst = models.BooleanField(default=False)
    # payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid'), ('Cancelled', 'Cancelled'), ('Partial Payment', 'Partial Payment')], default='Pending')
    is_sale = models.BooleanField(default=True)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.invoice_number} - {self.customer.name} -{self.order_date}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"