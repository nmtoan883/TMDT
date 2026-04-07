from django import forms
from .models import Product, Review, ContactMessage
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image']
        widgets = {
            'rating': forms.Select(
                choices=[(i, str(i)) for i in range(1, 6)],
                attrs={'class': 'review-control'}
            ),
            'comment': forms.Textarea(
                attrs={'rows': 4, 'class': 'review-control', 'placeholder': 'Viết cảm nhận của bạn...'}
            ),
            'image': forms.ClearableFileInput(attrs={'class': 'review-control'})
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Họ và tên',
                'style': 'height:46px; border-radius:6px;'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'Email',
                'style': 'height:46px; border-radius:6px;'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Số điện thoại',
                'style': 'height:46px; border-radius:6px;'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Chủ đề',
                'style': 'height:46px; border-radius:6px;'
            }),
            'message': forms.Textarea(attrs={
                'class': 'input',
                'placeholder': 'Nhập nội dung liên hệ...',
                'rows': 6,
                'style': 'border-radius:6px; padding-top:12px;'
            }),
        }