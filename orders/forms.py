from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('sepay', 'Sepay (quét QR)'),
        ('cod', 'Thanh toán khi nhận hàng'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='sepay',
        label='Cổng thanh toán',
    )

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'province',
            'district',
            'ward',
            'postal_code',
            'payment_method',
        ]
        labels = {
            'first_name': 'Ho',
            'last_name': 'Ten',
            'email': 'Email',
            'phone': 'So dien thoai',
            'address': 'So nha, ten duong',
            'province': 'Tinh/Thanh pho',
            'district': 'Quan/Huyen',
            'ward': 'Phuong/Xa',
            'postal_code': 'Ma buu dien',
            'payment_method': 'Phuong thuc thanh toan',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Nguyễn'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: Văn A'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: 0912345678'}),
            'address': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Số nhà, tên đường...'}),
            'province': forms.Select(choices=[('', 'Chọn Tỉnh/Thành phố')], attrs={'class': 'input'}),
            'district': forms.Select(choices=[('', 'Chọn Quận/Huyện')], attrs={'class': 'input'}),
            'ward': forms.Select(choices=[('', 'Chọn Phường/Xã')], attrs={'class': 'input'}),
            'postal_code': forms.TextInput(attrs={'class': 'input', 'placeholder': 'VD: 700000'}),
            'payment_method': forms.RadioSelect(),
        }
