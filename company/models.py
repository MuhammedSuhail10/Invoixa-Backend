from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    purchase_tax_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    sales_tax_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CompanyBankDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bank_details')
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=11)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    account_type = models.CharField(max_length=50, choices=[('savings', 'Savings'), ('current', 'Current'), ('fixed', 'Fixed Deposit')], default='savings')
    upi_qr_code = models.ImageField(upload_to='upi_qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"