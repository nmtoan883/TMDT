from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomerProfileForm, UserRegistrationForm, UserUpdateForm
from .models import CustomerProfile


def register(request):
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
def dashboard(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if not profile.province and profile.city:
        profile.province = profile.city
        profile.save(update_fields=['province'])

    is_editing = request.GET.get('edit') == '1'

    if request.method == 'POST':
        is_editing = True
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            saved_profile = profile_form.save(commit=False)
            saved_profile.city = saved_profile.province
            saved_profile.save()
            messages.success(request, 'Thông tin tài khoản đã được cập nhật.')
            return redirect('accounts:dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=profile)

    return render(
        request,
        'accounts/dashboard.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile,
            'is_editing': is_editing,
        },
    )
