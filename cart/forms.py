from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=20,
        label='Số lượng',
        widget=forms.NumberInput(attrs={'class': 'input cart-qty-input'})
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
