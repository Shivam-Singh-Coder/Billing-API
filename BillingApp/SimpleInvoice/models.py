from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import MinLengthValidator, RegexValidator, EmailValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from AuthorizationApp import models as auth_models

class SimpleInvoiceCustomer(models.Model):
    company = models.ForeignKey(auth_models.CompanyID, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(
        max_length=200,
    )
    phone = models.CharField(
        max_length=15,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=10, choices=APP_CHOICES, default='web')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['-created_at']

class SimpleInvoiceStockInventory(models.Model):
    company = models.ForeignKey(auth_models.CompanyID, on_delete=models.CASCADE, related_name='inventory')
    product_name = models.CharField(max_length=200,)
    unit = models.PositiveIntegerField(default=0)
    unit_type = models.ForeignKey('SimpleInvoiceMeasurementUnit', on_delete=models.CASCADE, related_name='stock_inventory')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=10, choices=APP_CHOICES, default='web')

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "Stock Inventory"
        verbose_name_plural = "Stock Inventories"
        ordering = ['-created_at']

class SimpleInvoiceMeasurementUnit(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=200,choices=APP_CHOICES, default='web')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Measurement Unit"
        verbose_name_plural = "Measurement Units"
        ordering = ['-created_at']

class SimpleInvoiceGenerateBill(models.Model):
    company = models.ForeignKey(auth_models.CompanyID, on_delete=models.CASCADE, related_name='generate_bill')
    invoice_number = models.CharField(max_length=200, unique=True)
    customer = models.ForeignKey(SimpleInvoiceCustomer, on_delete=models.CASCADE) #use for customer id
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grand_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=50,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=200, default='web', choices=APP_CHOICES)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-created_at']


class SimpleInvoiceBillItem(models.Model):
    invoice = models.ForeignKey(SimpleInvoiceGenerateBill, on_delete=models.CASCADE, related_name='items') #use for invoice id
    product = models.ForeignKey(SimpleInvoiceStockInventory, on_delete=models.CASCADE, related_name='invoice_items') #use for product id
    quantity = models.PositiveIntegerField()
    sub_unit = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=200, default='web', choices=APP_CHOICES)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} pcs"
    
    class Meta:
        verbose_name = "Simple Invoice Item"
        verbose_name_plural = "Simple Invoice Items"
        ordering = ['-created_at']

class SimpleInvoiceNumberGenerate(models.Model):
    company = models.ForeignKey(auth_models.CompanyID, on_delete=models.CASCADE, related_name='invoice_number_generator')
    last_invoice_number = models.BigIntegerField(default=0)

    def __str__(self):
        return str(self.software.company_name) + "- Invoice Number Generator"

    class Meta:
        verbose_name = "Invoice Number Generator"
        verbose_name_plural = "Invoice Number Generators"