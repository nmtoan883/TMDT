from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
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
            'address': 'So nha, ten duong',
            'province': 'Tinh/Thanh pho',
            'district': 'Quan/Huyen',
            'ward': 'Phuong/Xa',
            'postal_code': 'Ma buu dien',
            'payment_method': 'Phuong thuc thanh toan',
        }

        widgets = {
            'province': forms.Select(choices=[('', 'Chon tinh/thanh pho')]),
            'district': forms.Select(choices=[('', 'Chon quan/huyen')]),
            'ward': forms.Select(choices=[('', 'Chon phuong/xa')]),
            'payment_method': forms.RadioSelect(),
        }
