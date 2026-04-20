from django import forms
from .models import Product, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(
                attrs={'rows': 4, 'class': 'review-control', 'placeholder': 'Viết cảm nhận của bạn...'}
            ),
            'image': forms.ClearableFileInput(attrs={'class': 'review-control'})
        }