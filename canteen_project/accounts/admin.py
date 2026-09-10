# accounts/admin.py
from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # 'is_phone_verified' hata diya hai:
    list_display = ('username', 'phone_number', 'room_or_class', 'is_staff')
    search_fields = ('phone_number', 'username')