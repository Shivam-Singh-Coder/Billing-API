from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator, MinValueValidator, MaxLengthValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime
import uuid

class GroceryShopDetails(models.Model):
    # Mobile number validation (exactly 10 digits)
    phone_validator = RegexValidator(
        regex=r'^\d{10}$', 
        message="Phone number must be exactly 10 digits."
    )

    # Email validation (Django has built-in EmailValidator)
    email_validator = EmailValidator(message="Enter a valid email address.")

    shop_name = models.CharField(max_length=100,validators=[MinLengthValidator(3)])  # Enforces minimum length of 3 characters)
    shop_owner_name = models.CharField(max_length=100,validators=[MinLengthValidator(3)])  # Enforces minimum length of 3 characters)
    shop_phone = models.CharField(
        max_length=10, 
        validators=[phone_validator],
        unique=True
    )
    shop_email = models.EmailField(
        max_length=100, 
        validators=[email_validator], 
        null=True,
        blank=True
    )
    shop_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(max_length=100, choices=APP_CHOICES, default="Web")

    def __str__(self):
        return self.shop_name

    def clean(self):
        """Additional validation for fields"""
        super().clean()

        # Ensure phone is exactly 10 digits
        if not self.shop_phone.isdigit() or len(self.shop_phone) != 10:
            raise ValidationError({"shop_phone": "Phone number must be exactly 10 digits."})

        # Validate email only if provided (null=True allows it to be empty)
        if self.shop_email:
            try:
                self.email_validator(self.shop_email)
            except ValidationError:
                raise ValidationError({"shop_email": "Enter a valid email address."})
    def formatted_created_date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    def formatted_updated_date(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = "Grocery Shop Details"
        verbose_name_plural = "Grocery Shop Details"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['shop_name', 'shop_phone'], name="unique__grocery_shop_details")
        ]

class GroceryCategory(models.Model):
    category_name = models.CharField(
        max_length=100, 
        unique=True,  # Ensures category names are unique
        validators=[MinLengthValidator(3)]  # Enforces minimum length of 3 characters
    )
    category_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(max_length=100, choices=APP_CHOICES, default="Web")

    def __str__(self):
        return self.category_name

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensuring category name is not just spaces
        if not self.category_name.strip():
            raise ValidationError({"category_name": "Category name cannot be blank or spaces only."})
        
    def formatted_created_date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    def formatted_updated_date(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = "Grocery Category"
        verbose_name_plural = "Grocery Categories"
        ordering = ['-created_at']

class GroceryStockInventory(models.Model):
    category = models.ForeignKey(
        GroceryCategory, 
        on_delete=models.CASCADE, 
        related_name='stock_inventory'
    )
    shop = models.ForeignKey(
        GroceryShopDetails, 
        on_delete=models.CASCADE, 
        related_name='stock_inventory'
    )
    product_name = models.CharField(
        max_length=100, 
        validators=[MinLengthValidator(3)]
    )
    product_description = models.TextField(null=True, blank=True)
    product_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(1)]
    )  # Ensures price is at least 1 currency units

    product_quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )  # Ensures at least 1 unit is in stock

    margin_percent = models.IntegerField(default=0)
    discount_percent = models.IntegerField(default=0)
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )

    unit = models.CharField(max_length=100)

    expire_at = models.DateTimeField(null=True, blank=True)  # Allow manual expiration date input
    purchased_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(
        max_length=100, 
        choices=APP_CHOICES, 
        default="Web"
    )

    def __str__(self):
        return f"{self.product_name} - {self.shop.shop_name}"

    def formatted_created_date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def formatted_updated_date(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensure product price, purchase price, and sale price make sense
        if self.purchase_price < 0:
            raise ValidationError({"purchase_price": "Purchase price cannot be negative."})
        if self.sale_price < self.purchase_price:
            raise ValidationError({"sale_price": "Sale price cannot be less than purchase price."})

        # Ensure discount and margin percent are within a valid range
        if not (0 <= self.discount_percent <= 100):
            raise ValidationError({"discount_percent": "Discount percent must be between 0 and 100."})
        if not (0 <= self.margin_percent <= 100):
            raise ValidationError({"margin_percent": "Margin percent must be between 0 and 100."})

        # Ensure expiration date (if provided) is not in the past
        if self.expire_at and self.expire_at < datetime.now():
            raise ValidationError({"expire_at": "Expiration date cannot be in the past."})

    class Meta:
        verbose_name = "Grocery Stock Inventory"
        verbose_name_plural = "Grocery Stock Inventories"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['shop', 'product_name'], name="unique_grocery_product_per_shop")
        ]

class GroceryStock(models.Model):
    """Model for Grocery stock tracking"""
    
    grocery_stock_inventory = models.ForeignKey(
        GroceryStockInventory, 
        on_delete=models.CASCADE, 
        related_name="grocery_stock"
    )
    available_quantity = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)]
    )  # Cannot be negative

    purchased_quantity = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)]
    )  # Cannot be negative

    last_updated = models.DateTimeField(auto_now=True)

    def formatted_last_updated_date(self):
        return self.last_updated.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"{self.grocery_stock_inventory.product_name} - Available: {self.available_quantity}"

    class Meta:
        verbose_name = "Grocery Stock"
        verbose_name_plural = "Grocery Stocks"
        ordering = ["-last_updated"]

class GroceryMeasurement(models.Model):
    """Model for Grocery measurements"""
    
    name_of_unit = models.CharField(
        max_length=100, 
        unique=True,  # Prevents duplicate measurement units
        validators=[MinLengthValidator(2)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_of_unit
    
    def formatted_created_date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    def formatted_updated_date(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = "Grocery Measurement"
        verbose_name_plural = "Grocery Measurements"
        ordering = ['name_of_unit']

class GroceryCustomer(models.Model):
    """Model for Grocery customers"""

    customer_name = models.CharField(
        max_length=200, 
        validators=[MinLengthValidator(2)]
    )

    customer_phone = models.CharField(
        max_length=20, 
        unique=True,  # Ensures phone number is unique
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message="Phone number must be exactly 10 digits."
        )]
    )

    customer_email = models.EmailField(
        max_length=100, 
        null=True, 
        blank=True, 
        validators=[EmailValidator()]
    )

    customer_address = models.CharField(max_length=200)
    customer_gst = models.CharField(
        max_length=15, 
        null=True, 
        blank=True, 
        unique=True, 
        validators=[RegexValidator(
            regex=r'^[0-9A-Z]{15}$',
            message="GST must be a valid 15-character alphanumeric code."
        )]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(
        max_length=100, 
        choices=APP_CHOICES, 
        default="Web"
    )
    email_validator = EmailValidator(message="Enter a valid email address.")
    def __str__(self):
        return f"{self.customer_name} ({self.customer_phone})"

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensure at least one contact detail is provided
        if not self.customer_phone:
            raise ValidationError("Customer phone number is required.")
        if self.customer_email:
            try:
                self.email_validator(self.customer_email)
            except ValidationError:
                raise ValidationError({"customer_email": "Enter a valid email address."})
            
    def formatted_created_date(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    def formatted_updated_date(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = "Grocery Customer"
        verbose_name_plural = "Grocery Customers"
        ordering = ['-created_at']

class GroceryOrderDetails(models.Model):
    """Model for Grocery order details"""
    
    customer = models.ForeignKey(
        GroceryCustomer, 
        on_delete=models.CASCADE, 
        related_name="orders"
    )
    
    order_number = models.CharField(
        max_length=200, 
        unique=True  # Ensures unique order numbers
    )
    
    order_date = models.DateTimeField(auto_now_add=True)
    
    selected_product = models.ManyToManyField(
        'GroceryStockInventory', 
        through='GroceryOrderedProduct', 
        related_name="ordered_products"
    )

    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )

    pay_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )

    dues_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('placed', 'Placed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out For Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    order_status = models.CharField(
        max_length=100, 
        choices=ORDER_STATUS_CHOICES, 
        default="pending"
    )

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('due', 'Due'),
    ]
    payment_status = models.CharField(
        max_length=100, 
        choices=PAYMENT_STATUS_CHOICES, 
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(
        max_length=100, 
        choices=APP_CHOICES, 
        default="Web"
    )

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensure dues amount is correctly calculated
        if self.dues_amount != (self.total_amount - self.pay_amount):
            raise ValidationError({
                "dues_amount": "Dues amount must be equal to total_amount - pay_amount."
            })

    def __str__(self):
        return f"Order {self.order_number} - {self.customer.customer_name}"

    class Meta:
        verbose_name = "Grocery Order Detail"
        verbose_name_plural = "Grocery Order Details"
        ordering = ['-created_at']

class GroceryOrderedProduct(models.Model):
    """Model for products in an order"""
    
    order = models.ForeignKey(
        GroceryOrderDetails, 
        on_delete=models.CASCADE, 
        related_name="ordered_products"
    )
    
    product = models.ForeignKey(
        GroceryStockInventory, 
        on_delete=models.CASCADE, 
        related_name="orders"
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )  # Prevents negative or zero quantity

    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(1)]
    )  # Ensures product price is valid

    discount_percent = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Discount must be between 0 and 100

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(
        max_length=100, 
        choices=APP_CHOICES, 
        default="Web"
    )

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensure discount percentage is within range
        if self.discount_percent < 0 or self.discount_percent > 100:
            raise ValidationError({
                "discount_percent": "Discount must be between 0 and 100."
            })

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} units"

    class Meta:
        verbose_name = "Grocery Ordered Product"
        verbose_name_plural = "Grocery Ordered Products"

class GroceryOrderQuotation(models.Model):
    """Model for Grocery order quotations"""

    customer = models.ForeignKey(
        GroceryCustomer, 
        on_delete=models.CASCADE, 
        related_name="quotations"
    )

    quotation_number = models.CharField(
        max_length=200, 
        unique=True  # Ensures unique quotation numbers
    )

    quotation_date = models.DateTimeField(auto_now_add=True)

    selected_product = models.ManyToManyField(
        'GroceryStockInventory', 
        through='GroceryQuotationProduct', 
        related_name="quoted_products"
    )

    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )

    discount_percent = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Discount cannot exceed 100%

    final_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=100, 
        choices=STATUS_CHOICES, 
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(
        max_length=100, 
        choices=APP_CHOICES, 
        default="Web"
    )

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensure final amount accounts for discount
        discounted_amount = self.total_amount * (1 - (self.discount_percent / 100))
        if self.final_amount != discounted_amount:
            raise ValidationError({
                "final_amount": "Final amount must be total_amount after discount."
            })

    def __str__(self):
        return f"Quotation {self.quotation_number} - {self.customer.customer_name}"

    class Meta:
        verbose_name = "Grocery Order Quotation"
        verbose_name_plural = "Grocery Order Quotations"
        ordering = ['-created_at']

class GroceryQuotationProduct(models.Model):
    """Model for products in a quotation"""

    quotation = models.ForeignKey(
        GroceryOrderQuotation, 
        on_delete=models.CASCADE, 
        related_name="quoted_products"
    )

    product = models.ForeignKey(
        GroceryStockInventory, 
        on_delete=models.CASCADE, 
        related_name="quotations"
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(1)]
    )

    discount_percent = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    APP_CHOICES = [
        ('Mobile', 'Mobile App'),
        ('Web', 'Web App'),
    ]
    app_name = models.CharField(
        max_length=100, 
        choices=APP_CHOICES, 
        default="Web"
    )

    def clean(self):
        """Custom validation logic"""
        super().clean()

        # Ensure discount percentage is within range
        if self.discount_percent < 0 or self.discount_percent > 100:
            raise ValidationError({
                "discount_percent": "Discount must be between 0 and 100."
            })

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} units"

    class Meta:
        verbose_name = "Grocery Quotation Product"
        verbose_name_plural = "Grocery Quotation Products"