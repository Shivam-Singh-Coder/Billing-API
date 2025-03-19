from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Custom fields to relate users to different apps
    SOFTWARE_TYPE = [
        ('garments', 'Garments'),
        ('grocery', 'Grocery'),
        ('jewellery', 'Jewellery'),
        ('medical', 'Medical'),
    ]
    software_type = models.CharField(max_length=255, choices=SOFTWARE_TYPE,default='gm')

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        constraints = [
            models.UniqueConstraint(fields=['username', 'software_type'], name='unique_username_software_type')
        ]

