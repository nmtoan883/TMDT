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
        }

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ho'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ten'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Dia chi'}),
            'province': forms.Select(choices=[('', 'Chon tinh/thanh pho')], attrs={'class': 'input'}),
            'district': forms.Select(choices=[('', 'Chon quan/huyen')], attrs={'class': 'input'}),
            'ward': forms.Select(choices=[('', 'Chon phuong/xa')], attrs={'class': 'input'}),
        }
