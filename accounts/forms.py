from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import CustomerProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Mat khau',
        widget=forms.PasswordInput(attrs={'placeholder': 'It nhat 8 ky tu'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Xac nhan mat khau',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nhap lai mat khau'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Ten dang nhap',
            'first_name': 'Ho',
            'last_name': 'Ten',
            'email': 'Email',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email nay da duoc su dung. Vui long dung email khac.')
        return email

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise ValidationError('Hai mat khau khong khop nhau.')
        return cd.get('password2')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and password.isdigit():
            raise ValidationError('Mat khau khong duoc chi toan so.')
        return password


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Họ',
            'last_name': 'Tên',
            'email': 'Email',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if email and qs.exists():
            raise ValidationError('Email nay da duoc su dung.')
        return email


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address', 'province', 'district', 'ward', 'postal_code', 'avatar']
        labels = {
            'phone': 'Số điện thoại',
            'address': 'Địa chỉ nhà',
            'province': 'Tỉnh/Thành phố',
            'district': 'Quận/Huyện',
            'ward': 'Phường/Xã',
            'postal_code': 'Mã bưu điện',
            'avatar': 'Ảnh đại diện',
        }

        widgets = {
            'province': forms.Select(choices=[('', 'Chọn tỉnh/thành phố')]),
            'district': forms.Select(choices=[('', 'Chọn quận/huyện')]),
            'ward': forms.Select(choices=[('', 'Chọn phường/xã')]),
        }
