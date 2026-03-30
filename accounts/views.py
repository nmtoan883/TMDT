from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

from .forms import UserRegistrationForm

def register(request):
    """Xử lý đăng ký tài khoản mới."""
    if request.user.is_authenticated:
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Chào mừng {new_user.username}! Tài khoản của bạn đã được tạo thành công.')
            return redirect('shop:product_list')
    else:
        form = UserRegistrationForm()


