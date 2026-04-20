import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='categories/%Y/%m/%d', blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

    @property
    def category_image_url(self):
        if self.image:
            return self.image.url
        return '/static/img/category_placeholder.png'

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    brand = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    discount_percent = models.PositiveSmallIntegerField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=10)
    available = models.BooleanField(default=True)
    is_hotdeal = models.BooleanField(default=False)
    hotdeal_start = models.DateTimeField(blank=True, null=True)
    hotdeal_end = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

    def _active_prefetched_campaign(self):
        campaigns = getattr(self, '_prefetched_objects_cache', {}).get('hotdeal_campaigns')
        if campaigns is None:
            return None

        now = timezone.now()
        active_campaigns = [
            campaign for campaign in campaigns
            if campaign.is_active
            and campaign.start_at <= now
            and campaign.end_at >= now
        ]
        if not active_campaigns:
            return None
        active_campaigns.sort(key=lambda campaign: (campaign.priority, campaign.end_at, campaign.id))
        return active_campaigns[0]

    @property
    def active_hotdeal_campaign(self):
        prefetched_campaign = self._active_prefetched_campaign()
        if prefetched_campaign is not None:
            return prefetched_campaign

        now = timezone.now()
        return (
            self.hotdeal_campaigns.filter(
                is_active=True,
                start_at__lte=now,
                end_at__gte=now,
            )
            .order_by('priority', 'end_at', 'id')
            .first()
        )

    def clean(self):
        if self.is_hotdeal:
            if not self.discount_percent:
                raise ValidationError({'discount_percent': 'Vui lòng nhập phần trăm giảm giá khi bật Hot Deal.'})
            if self.discount_percent < 1 or self.discount_percent > 99:
                raise ValidationError({'discount_percent': 'Phần trăm giảm giá phải nằm trong khoảng 1 đến 99.'})
            if not self.hotdeal_end:
                raise ValidationError({'hotdeal_end': 'Vui lòng chọn thời gian kết thúc cho Hot Deal.'})
            if self.hotdeal_start and self.hotdeal_end and self.hotdeal_start >= self.hotdeal_end:
                raise ValidationError({'hotdeal_end': 'Thời gian kết thúc phải sau thời gian bắt đầu.'})
        elif self.discount_percent:
            raise ValidationError({'discount_percent': 'Hãy bật Hot Deal nếu muốn sử dụng phần trăm giảm giá.'})

    @property
    def is_hotdeal_active(self):
        if self.active_hotdeal_campaign:
            return True
        if not self.is_hotdeal or not self.discount_percent:
            return False
        now = timezone.now()
        if self.hotdeal_start and self.hotdeal_start > now:
            return False
        if self.hotdeal_end and self.hotdeal_end < now:
            return False
        return True

    @property
    def hotdeal_price(self):
        discount_percent = self.display_discount_percent
        if not discount_percent:
            return None
        base_price = getattr(self, 'base_price', self.price)
        discount_value = (base_price * Decimal(discount_percent) / Decimal('100')).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP,
        )
        discounted_price = (base_price - discount_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return max(discounted_price, Decimal('0.00'))

    @property
    def display_price(self):
        base_price = getattr(self, 'base_price', self.price)
        return self.hotdeal_price if self.is_hotdeal_active and self.hotdeal_price is not None else base_price

    @property
    def display_old_price(self):
        if self.is_hotdeal_active and self.hotdeal_price is not None:
            return getattr(self, 'base_price', self.price)
        return getattr(self, 'base_old_price', self.old_price)

    @property
    def display_discount_percent(self):
        active_campaign = self.active_hotdeal_campaign
        if active_campaign:
            return active_campaign.discount_percent
        return self.discount_percent if self.is_hotdeal_active else None

    @property
    def effective_hotdeal_start(self):
        active_campaign = self.active_hotdeal_campaign
        if active_campaign:
            return active_campaign.start_at
        return self.hotdeal_start

    @property
    def effective_hotdeal_end(self):
        active_campaign = self.active_hotdeal_campaign
        if active_campaign:
            return active_campaign.end_at
        return self.hotdeal_end


class HotDealCampaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveSmallIntegerField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=0)
    products = models.ManyToManyField(Product, related_name='hotdeal_campaigns', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'start_at', '-created']

    def __str__(self):
        return self.name

    def clean(self):
        if self.discount_percent < 1 or self.discount_percent > 99:
            raise ValidationError({'discount_percent': 'Phần trăm giảm giá phải nằm trong khoảng 1 đến 99.'})
        if self.start_at >= self.end_at:
            raise ValidationError({'end_at': 'Thời gian kết thúc phải sau thời gian bắt đầu.'})

    @property
    def is_running(self):
        now = timezone.now()
        return self.is_active and self.start_at <= now <= self.end_at

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/%Y/%m/%d', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.name}'

class Policy(models.Model):
    POLICY_TYPES = (
        ('warranty', 'Bảo hành'),
        ('return', 'Đổi trả'),
        ('shipping', 'Vận chuyển'),
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)

    def __str__(self):
        return self.title

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlist_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlist_items', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tin nhắn liên hệ'
        verbose_name_plural = 'Tin nhắn liên hệ'

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
    
class ContactInfo(models.Model):
    title = models.CharField(max_length=200, default='Liên hệ với chúng tôi')
    description = models.TextField(blank=True)

    address = models.CharField(max_length=255)
    hotline = models.CharField(max_length=20)
    email = models.EmailField()
    working_hours = models.CharField(max_length=255, blank=True)

    map_embed_url = models.TextField(
        help_text='Dán link Google Maps embed'
    )

    support_1 = models.CharField(max_length=255, blank=True)
    support_2 = models.CharField(max_length=255, blank=True)
    support_3 = models.CharField(max_length=255, blank=True)
    support_4 = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Thông tin liên hệ"


class LiveChatSession(models.Model):
    session_key = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Live Chat Session'
        verbose_name_plural = 'Live Chat Sessions'

    def __str__(self):
        return f"Chat Session: {str(self.session_key)[:8]}"

class LiveChatMessage(models.Model):
    session = models.ForeignKey(LiveChatSession, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        prefix = 'Admin' if self.is_admin else 'User'
        return f"{prefix}: {self.content[:30]}"

class Banner(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/%Y/%m/%d')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Banner Trang Chủ'
        verbose_name_plural = 'Banners Trang Chủ'

    def __str__(self):
        return self.title

