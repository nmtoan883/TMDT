from django.contrib.auth.models import User
from django.db import models
from core.models import Product


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SHIPPING = 'shipping'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Cho duyet'),
        (STATUS_SHIPPING, 'Dang giao'),
        (STATUS_CANCELLED, 'Da huy'),
    ]

    PAYMENT_COD = 'cod'
    PAYMENT_SEPAY = 'sepay'
    PAYMENT_CHOICES = [
        (PAYMENT_COD, 'Thanh toan khi nhan hang'),
        (PAYMENT_SEPAY, 'Thanh toan qua SePay'),
    ]

    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    ward = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_COD)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

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
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
