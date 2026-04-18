from django.db import models
from django.utils import timezone
from django.urls import reverse


class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Giảm theo phần trăm'),
        ('amount', 'Giảm theo số tiền'),
        ('label', 'Nhãn ưu đãi'),
    )

    title = models.CharField(max_length=255, verbose_name='Tên chương trình')
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300, verbose_name='Mô tả ngắn')
    content = models.TextField(blank=True, null=True, verbose_name='Nội dung chi tiết')
    banner_image = models.ImageField(upload_to='promotions/', blank=True, null=True, verbose_name='Ảnh banner')

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        verbose_name='Loại ưu đãi'
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Giá trị ưu đãi'
    )
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nhãn hiển thị')

    start_date = models.DateTimeField(verbose_name='Ngày bắt đầu')
    end_date = models.DateTimeField(verbose_name='Ngày kết thúc')

    is_featured = models.BooleanField(default=False, verbose_name='Ưu đãi nổi bật')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    products = models.ManyToManyField(
        'core.Product',
        blank=True,
        related_name='promotions',
        verbose_name='Sản phẩm áp dụng'
    )

    coupon = models.ForeignKey(
        'coupon.Coupon',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='promotions',
        verbose_name='Mã giảm giá liên kết'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Khuyến mãi'
        verbose_name_plural = 'Khuyến mãi'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('promotions:promotion_detail', kwargs={'slug': self.slug})

    @property
    def is_current(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def display_badge(self):
        if self.discount_type == 'percent' and self.discount_value:
            return f"-{int(self.discount_value)}%"
        if self.discount_type == 'amount' and self.discount_value:
            return f"Giảm {int(self.discount_value):,}đ".replace(',', '.')
        if self.label:
            return self.label
        return "Ưu đãi"