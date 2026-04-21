import secrets
import string

from django import forms
from django.utils import timezone
from blog.models import Post
from core.models import Banner, HotDealCampaign, Product
from coupon.models import Coupon

COUPON_CODE_LENGTH = 16

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'category', 'image', 'summary', 'content', 'author', 'is_published', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề...'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Để trống để tự động sinh'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Một đoạn tóm tắt ngắn...'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Note: content uses RichTextUploadingField, Django will automatically use the CKEditor widget
        }

from django.contrib.auth.models import User
from accounts.models import CustomerProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, help_text="Bỏ trống nếu không muốn đổi mật khẩu")
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address', 'ward', 'district', 'province', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

from legal.models import PolicyPage, BusinessLicense

class PolicyPageForm(forms.ModelForm):
    class Meta:
        model = PolicyPage
        fields = ['policy_type', 'title', 'slug', 'content', 'is_published']
        widgets = {
            'policy_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BusinessLicenseForm(forms.ModelForm):
    class Meta:
        model = BusinessLicense
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_code': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'representative': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'link', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'brand', 'image', 'description', 'price', 'old_price', 'stock', 'available']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HotDealCampaignAdminForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Sản phẩm áp dụng',
    )

    class Meta:
        model = HotDealCampaign
        fields = ['name', 'description', 'discount_percent', 'start_at', 'end_at', 'is_active', 'priority', 'products']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '99'}),
            'start_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datetime_formats = ['%Y-%m-%dT%H:%M']
        self.fields['start_at'].input_formats = datetime_formats
        self.fields['end_at'].input_formats = datetime_formats

        for field_name in ('start_at', 'end_at'):
            value = self.initial.get(field_name) or getattr(self.instance, field_name, None)
            if value:
                self.initial[field_name] = timezone.localtime(value).strftime('%Y-%m-%dT%H:%M')


class CouponAdminForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=500,
        initial=1,
        label='Số lượng mã',
        help_text='Nhập số mã cần tạo. Mỗi mã sẽ tự sinh 16 ký tự in hoa và số.',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '500',
            'placeholder': 'VD: 10',
        })
    )

    class Meta:
        model = Coupon
        fields = ['discount_percent', 'valid_to', 'active']
        labels = {
            'discount_percent': 'Giảm theo phần trăm',
            'valid_to': 'Kết thúc',
            'active': 'Đang bật',
        }
        widgets = {
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '99', 'placeholder': 'VD: 20'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datetime_formats = ['%Y-%m-%dT%H:%M']
        self.fields['valid_to'].input_formats = datetime_formats

        if self.instance and self.instance.pk:
            self.fields.pop('quantity', None)

        value = self.initial.get('valid_to') or getattr(self.instance, 'valid_to', None)
        if value:
            self.initial['valid_to'] = timezone.localtime(value).strftime('%Y-%m-%dT%H:%M')

    def _generate_code(self, reserved_codes=None):
        reserved_codes = reserved_codes or set()
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(COUPON_CODE_LENGTH))
            if code not in reserved_codes and not Coupon.objects.filter(code=code).exists():
                return code

    def save_many(self):
        if self.instance and self.instance.pk:
            return [self.save()]

        quantity = self.cleaned_data.get('quantity') or 1
        coupons = []
        generated_codes = set()
        now = timezone.now()

        for _ in range(quantity):
            code = self._generate_code(generated_codes)
            generated_codes.add(code)
            coupons.append(Coupon(
                code=code,
                discount_percent=self.cleaned_data['discount_percent'],
                discount_amount=None,
                valid_from=now,
                valid_to=self.cleaned_data['valid_to'],
                active=self.cleaned_data.get('active', True),
            ))

        Coupon.objects.bulk_create(coupons)
        return coupons

    def clean(self):
        cleaned = super().clean()
        discount_percent = cleaned.get('discount_percent')
        valid_to = cleaned.get('valid_to')

        if not discount_percent:
            self.add_error('discount_percent', 'Vui lòng nhập phần trăm giảm.')
        if discount_percent and discount_percent > 99:
            self.add_error('discount_percent', 'Phần trăm giảm phải nhỏ hơn 100.')
        if valid_to and valid_to <= timezone.now():
            self.add_error('valid_to', 'Ngày hết hạn phải ở tương lai.')

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.discount_amount = None
        if not instance.pk:
            instance.code = self._generate_code()
            instance.valid_from = timezone.now()
        if commit:
            instance.save()
        return instance

