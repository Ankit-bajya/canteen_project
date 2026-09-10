# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=10, unique=True)
    room_or_class = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Room 102 / B.Tech CS 3rd Year")

    # Login mobile number ya username kisi se bhi kara sakte hain
    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return f"{self.username} ({self.phone_number})"