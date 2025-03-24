from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator, EmailValidator

class User(AbstractUser):
    software_type = models.ForeignKey('SoftwareType', on_delete=models.CASCADE, related_name='users',null=True)
    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=10,choices=APP_CHOICES, default='web')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        constraints = [
            models.UniqueConstraint(fields=['username', 'software_type'], name='unique_username_software_type')
        ]

class SoftwareType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=10,choices=APP_CHOICES, default='web')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Software Type"
        verbose_name_plural = "Software Types"
        ordering = ['-created_at']

class CompanyID(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_details')
    company_name = models.CharField(max_length=200)
    company_number = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^\d{7,15}$', message="Phone number must be between 7 to 15 digits and contain only numbers.")])
    email = models.EmailField(max_length=100, blank=True, null=True, validators=[EmailValidator(message="Please enter a valid email address.")])
    address = models.TextField()
    invoice_code = models.CharField(max_length=200)  # v1,v2
    expire_days = models.PositiveIntegerField(default=0,null=True,blank=True)
    software_type = models.ForeignKey(SoftwareType, on_delete=models.CASCADE, related_name='software_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    APP_CHOICES = [
        ('web', 'Web App'),
        ('mobile', 'Mobile App'),
    ]
    app_name = models.CharField(max_length=200, default='web', choices=APP_CHOICES)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Software"
        verbose_name_plural = "Softwares"
        ordering = ['-created_at']

