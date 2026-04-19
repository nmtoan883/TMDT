from django.db import models
from django.urls import reverse


class PolicyPage(models.Model):
    POLICY_CHOICES = (
        ('return', 'Chính sách đổi trả'),
        ('shipping', 'Chính sách vận chuyển'),
        ('warranty', 'Chính sách bảo hành'),
        ('privacy', 'Chính sách bảo mật'),
        ('terms', 'Điều khoản sử dụng'),
        ('payment', 'Quy trình mua hàng và thanh toán'),
        ('complaint', 'Khiếu nại và giải quyết tranh chấp'),
    )

    policy_type = models.CharField(max_length=20, choices=POLICY_CHOICES, unique=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Trang chính sách'
        verbose_name_plural = 'Trang chính sách'
        ordering = ['policy_type']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('legal:policy_detail', kwargs={'slug': self.slug})


class BusinessLicense(models.Model):
    company_name = models.CharField(max_length=255, verbose_name='Tên doanh nghiệp')
    business_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Tên cửa hàng / thương hiệu')
    tax_code = models.CharField(max_length=50, verbose_name='Mã số thuế')
    license_number = models.CharField(max_length=100, verbose_name='Số giấy phép kinh doanh')
    issued_by = models.CharField(max_length=255, verbose_name='Nơi cấp')
    issue_date = models.DateField(verbose_name='Ngày cấp')
    address = models.CharField(max_length=255, verbose_name='Địa chỉ')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số điện thoại')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    representative = models.CharField(max_length=255, blank=True, null=True, verbose_name='Người đại diện')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả thêm')
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Giấy phép kinh doanh'
        verbose_name_plural = 'Giấy phép kinh doanh'

    def __str__(self):
        return self.company_name