# dashboard/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100) # e.g., Cold Drink, Chips & Kurkure, Junk Food
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name


class Brand(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='brands')
    name = models.CharField(max_length=100) # e.g., Lays, Kurkure, Coca Cola, Pepsi

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    
    name = models.CharField(max_length=150) # e.g., Lays Cream & Onion 20rs
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='items/')
    
    # Status Boolean: True = Colorful (Available), False = Grayscale/Colorless (Out of Stock)
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({'In Stock' if self.is_available else 'Out of Stock'})"


# dashboard/models.py

class Order(models.Model):
    LOCATION_CHOICES = (
        ('C1_BOYS', 'C 1 Boys Hostel (Gate)'),
        ('C2_GIRLS', 'C 2 Girls Hostel (Gate)'),
        ('C3_BOYS', 'C 3 Boys Hostel (Gate)'),
        ('C4_BOYS', 'C 4 Boys Hostel (Gate)'),
        ('C5_GIRLS', 'C 5 Girls Hostel (Gate)'),
        ('C6_BOYS', 'C 6 Boys Hostel (Gate)'),
        ('CAMPUS_OTHER', 'Other Location in Campus'),
        ('TAKEAWAY', 'Self Pickup (Canteen)'),
    )

    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment / UPI'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD')
    
    delivery_location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='C1_BOYS')
    # Custom spot ya landmark ke liye text field
    specific_spot = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Lawn near C1, Ground bench, etc.")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.user.phone_number})"  

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"  


# dashboard/models.py me bottom par add karein

class Notification(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.title}"        