from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm

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

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Hiển thị và cập nhật thông tin cá nhân."""
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thông tin cá nhân đã được cập nhật.')
            return redirect('accounts:profile')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
