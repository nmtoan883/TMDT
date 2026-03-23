from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    """Form đăng ký tài khoản mới với kiểm tra đầy đủ."""
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
        """Kiểm tra email đã tồn tại trong hệ thống chưa."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email này đã được sử dụng. Vui lòng dùng email khác.')
        return email

    def clean_password2(self):
        """Kiểm tra hai mật khẩu có khớp nhau không."""
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise ValidationError('Hai mật khẩu không khớp nhau.')
        return cd.get('password2')

    def clean_password(self):
        """Kiểm tra mật khẩu không quá đơn giản."""
        password = self.cleaned_data.get('password')
        if password and password.isdigit():
            raise ValidationError('Mật khẩu không được chỉ toàn số.')
        return password


class UserEditForm(forms.ModelForm):
    """Form chỉnh sửa thông tin cá nhân."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Họ',
            'last_name': 'Tên',
            'email': 'Email',
        }
