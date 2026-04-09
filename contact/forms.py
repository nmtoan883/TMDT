from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập họ và tên'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số điện thoại'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập nội dung liên hệ',
                'rows': 5
            }),
        }