from django.contrib.auth.models import User
from django.db import models


from core.models import Product

# ======================
# ORDER
# ======================


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    email = models.EmailField(default="")
    address = models.CharField(max_length=250, default="")
    postal_code = models.CharField(max_length=20, default="")
    province = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


# ======================
# ORDER ITEM
# ======================

    def get_status_label_class(self):
        return {
            self.STATUS_PENDING: 'warning',
            self.STATUS_SHIPPING: 'primary',
            self.STATUS_CANCELLED: 'danger',
        }.get(self.status, 'secondary')

    @property
    def province_display(self):
        return self.province or self.city

    @property
    def full_address(self):
        parts = [self.address, self.ward, self.district, self.province_display]
        return ', '.join(part for part in parts if part)

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"