from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import CustomerProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ít nhất 8 ký tự'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nhập lại mật khẩu'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Tên đăng nhập',
            'first_name': 'Họ',
            'last_name': 'Tên',
            'email': 'Email',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email này đã được sử dụng. Vui lòng dùng email khác.')
        return email

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise ValidationError('Hai mật khẩu không khớp nhau.')
        return cd.get('password2')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and password.isdigit():
            raise ValidationError('Mật khẩu không được chỉ toàn số.')
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
            raise ValidationError('Email này đã được sử dụng.')
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

class CustomSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='Họ', widget=forms.TextInput(attrs={'placeholder': 'Họ của bạn'}))
    last_name = forms.CharField(max_length=30, label='Tên', widget=forms.TextInput(attrs={'placeholder': 'Tên của bạn'}))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

