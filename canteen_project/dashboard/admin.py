# dashboard/admin.py
from django.contrib import admin
from .models import Category, Brand, Item

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'brand', 'price', 'is_available')
    list_editable = ('is_available',) # Admin panel se hi directly On/Off (Stock) switch kar sakte ho
    list_filter = ('is_available', 'category', 'brand')
    search_fields = ('name',)