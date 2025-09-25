# traceability/models.py
# Currently using blockchain/file-based storage instead of database models
# These models are defined for future database integration

from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Keeping models commented out for now since we're using file-based storage
# Uncomment and run migrations when ready to switch to database

"""
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Product Name")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    quantity = models.IntegerField(verbose_name="Quantity")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Product Image")
    batch_number = models.CharField(max_length=100, unique=True, verbose_name="Batch Number")
    expiry_date = models.DateField(verbose_name="Expiry Date")
    manufacturer = models.CharField(max_length=200, verbose_name="Manufacturer")
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    blockchain_hash = models.CharField(max_length=256, null=True, blank=True)
    
    class Meta:
        ordering = ['-date_created']
        verbose_name = "Drug Product"
        verbose_name_plural = "Drug Products"
    
    def __str__(self):
        return f"{self.name} - Batch: {self.batch_number}"

class TracingRecord(models.Model):
    TRACING_TYPES = [
        ('MANUFACTURED', 'Manufacturing'),
        ('QUALITY_TESTED', 'Quality Testing'),
        ('SHIPPED', 'Shipped'),
        ('RECEIVED', 'Received'),
        ('DISTRIBUTED', 'Distributed'),
        ('DISPENSED', 'Dispensed'),
        ('RETURNED', 'Returned'),
        ('RECALLED', 'Recalled'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tracing_records')
    tracing_type = models.CharField(max_length=20, choices=TRACING_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    location = models.CharField(max_length=200, verbose_name="Location/Facility")
    responsible_person = models.CharField(max_length=200, verbose_name="Responsible Person")
    notes = models.TextField(null=True, blank=True, verbose_name="Additional Notes")
    date_recorded = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    blockchain_hash = models.CharField(max_length=256, null=True, blank=True)
    previous_hash = models.CharField(max_length=256, null=True, blank=True)
    
    class Meta:
        ordering = ['-date_recorded']
        verbose_name = "Tracing Record"
        verbose_name_plural = "Tracing Records"
    
    def __str__(self):
        return f"{self.product.name} - {self.get_tracing_type_display()} ({self.status})"

class UserProfile(models.Model):
    USER_ROLES = [
        ('admin', 'Administrator'),
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('pharmacy', 'Pharmacy'),
        ('hospital', 'Hospital'),
        ('regulatory', 'Regulatory Authority'),
        ('quality_control', 'Quality Control'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='pharmacy')
    company_name = models.CharField(max_length=200, null=True, blank=True)
    license_number = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class AuditLog(models.Model):
    ACTION_TYPES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VIEW', 'Viewed'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
    
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} {self.object_type} at {self.timestamp}"
"""

# Simple data classes for current file-based system
class ProductData:
    """Simple data structure for products in file-based storage"""
    def __init__(self, name, price, qty, desc, image, last_update, tracing_info):
        self.name = name
        self.price = price
        self.qty = qty
        self.desc = desc
        self.image = image
        self.last_update = last_update
        self.tracing_info = tracing_info
