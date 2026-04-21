from django.contrib.auth.models import User
from django.db import models


from core.models import Product

# ======================
# ORDER
# ======================


class Order(models.Model):
    STATUS_PENDING    = 'pending'      # Chờ thanh toán
    STATUS_CONFIRMED  = 'confirmed'    # Đã TT – Chờ shop xác nhận
    STATUS_PREPARING  = 'preparing'    # Chờ lấy hàng (đang đóng gói)
    STATUS_SHIPPING   = 'shipping'     # Đang giao hàng
    STATUS_COMPLETED  = 'completed'    # Đã giao hàng thành công
    STATUS_CANCELLED  = 'cancelled'    # Đã huỷ
    STATUS_PROCESSING = 'processing'   # Giữ lại để tương thích

    STATUS_CHOICES = [
        (STATUS_PENDING,   'Chờ thanh toán'),
        (STATUS_CONFIRMED, 'Chờ xác nhận'),
        (STATUS_PREPARING, 'Chờ lấy hàng'),
        (STATUS_SHIPPING,  'Đang giao hàng'),
        (STATUS_COMPLETED, 'Đã giao hàng'),
        (STATUS_CANCELLED, 'Đã huỷ'),
        (STATUS_PROCESSING,'Đang xử lý'),   # tương thích cũ
    ]

    PAYMENT_COD = 'cod'
    PAYMENT_SEPAY = 'sepay'
    PAYMENT_CHOICES = [
        (PAYMENT_COD, 'Thanh toan khi nhan hang'),
        (PAYMENT_SEPAY, 'Thanh toan qua SePay'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True,
    )
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_COD)

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    email = models.EmailField(default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    address = models.CharField(max_length=250, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")
    province = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    PAYMENT_SEPAY = 'sepay'
    PAYMENT_MANUAL = 'manual'

    PAYMENT_CHOICES = [
        (PAYMENT_SEPAY, 'Sepay (QR code)'),
        (PAYMENT_MANUAL, 'Thanh toán thủ công / Admin duyệt'),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_SEPAY,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def created(self):
        return self.created_at

    def get_total_cost(self):
        items_total = sum(item.get_cost() for item in self.items.all())
        return items_total or self.total_amount


    def get_status_label_class(self):
        return {
            self.STATUS_PENDING: 'warning',
            self.STATUS_PROCESSING: 'primary',
            self.STATUS_COMPLETED: 'success',
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

    def get_cost(self):
        return self.price * self.quantity
