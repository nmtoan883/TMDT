from django import forms


class CouponApplyForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        label='Mã giảm giá',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Nhập mã giảm giá'
        })
    )