from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# Ensure only staff (Admins) can see dashboard
@staff_member_required
def index(request):
    return render(request, 'dasher_admin/index.html')

@staff_member_required
def blog_list(request):
    from blog.models import Post
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'dasher_admin/pages/blog/list.html', {'posts': posts})

@staff_member_required
def blog_add(request):
    from dasher_admin.forms import PostForm
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo bài viết thành công.')
            return redirect('dasher_admin:blog_list')
    else:
        form = PostForm()
    return render(request, 'dasher_admin/pages/blog/post_form.html', {'form': form})

@staff_member_required
def blog_edit(request, pk):
    from blog.models import Post
    from dasher_admin.forms import PostForm
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật bài viết thành công.')
            return redirect('dasher_admin:blog_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'dasher_admin/pages/blog/post_form.html', {'form': form, 'post': post})

@staff_member_required
def blog_delete(request, pk):
    from blog.models import Post
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, 'Đã xóa bài viết.')
    return redirect('dasher_admin:blog_list')

@staff_member_required
def blog_category_list(request):
    from blog.models import Category
    categories = Category.objects.all()
    return render(request, 'dasher_admin/pages/blog/category_list.html', {'categories': categories})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@staff_member_required
def blog_category_add(request):
    from blog.models import Category
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        Category.objects.create(name=name, slug=slug)
        messages.success(request, 'Đã tạo danh mục thành công.')
        return redirect('dasher_admin:blog_category_list')
    return render(request, 'dasher_admin/pages/blog/category_form.html')

@staff_member_required
def blog_category_edit(request, pk):
    from blog.models import Category
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.save()
        messages.success(request, 'Đã cập nhật danh mục thành công.')
        return redirect('dasher_admin:blog_category_list')
    return render(request, 'dasher_admin/pages/blog/category_form.html', {'category': category})

@staff_member_required
def blog_category_delete(request, pk):
    from blog.models import Category
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Đã xóa danh mục.')
    return redirect('dasher_admin:blog_category_list')

@staff_member_required
def account_list(request):
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dasher_admin/pages/accounts/list.html', {'users': users})

@staff_member_required
def account_add(request):
    from dasher_admin.forms import UserForm, CustomerProfileForm
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = CustomerProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Đã tạo tài khoản thành công.')
            return redirect('dasher_admin:account_list')
    else:
        user_form = UserForm()
        profile_form = CustomerProfileForm()
    return render(request, 'dasher_admin/pages/accounts/form.html', {'user_form': user_form, 'profile_form': profile_form})

@staff_member_required
def account_edit(request, pk):
    from django.contrib.auth.models import User
    from dasher_admin.forms import UserForm, CustomerProfileForm
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=user.customer_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            profile_form.save()
            messages.success(request, 'Đã cập nhật tài khoản thành công.')
            return redirect('dasher_admin:account_list')
    else:
        user_form = UserForm(instance=user)
        profile_form = CustomerProfileForm(instance=user.customer_profile)
    return render(request, 'dasher_admin/pages/accounts/form.html', {'user_form': user_form, 'profile_form': profile_form, 'account': user})

@staff_member_required
def account_delete(request, pk):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser:
        user.delete()
        messages.success(request, 'Đã xóa tài khoản.')
    else:
        messages.error(request, 'Không thể xóa tài khoản Quản trị viên tối cao.')
    return redirect('dasher_admin:account_list')

# Legal Policies
@staff_member_required
def legal_policy_list(request):
    from legal.models import PolicyPage
    policies = PolicyPage.objects.all().order_by('policy_type')
    return render(request, 'dasher_admin/pages/legal/policy_list.html', {'policies': policies})

@staff_member_required
def legal_policy_add(request):
    from dasher_admin.forms import PolicyPageForm
    if request.method == 'POST':
        form = PolicyPageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo sách sách thành công.')
            return redirect('dasher_admin:legal_policy_list')
    else:
        form = PolicyPageForm()
    return render(request, 'dasher_admin/pages/legal/policy_form.html', {'form': form})

@staff_member_required
def legal_policy_edit(request, pk):
    from legal.models import PolicyPage
    from dasher_admin.forms import PolicyPageForm
    policy = get_object_or_404(PolicyPage, pk=pk)
    if request.method == 'POST':
        form = PolicyPageForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật chính sách thành công.')
            return redirect('dasher_admin:legal_policy_list')
    else:
        form = PolicyPageForm(instance=policy)
    return render(request, 'dasher_admin/pages/legal/policy_form.html', {'form': form, 'policy': policy})

@staff_member_required
def legal_policy_delete(request, pk):
    from legal.models import PolicyPage
    policy = get_object_or_404(PolicyPage, pk=pk)
    policy.delete()
    messages.success(request, 'Đã xóa chính sách.')
    return redirect('dasher_admin:legal_policy_list')

# Legal Licenses
@staff_member_required
def legal_license_list(request):
    from legal.models import BusinessLicense
    licenses = BusinessLicense.objects.all()
    return render(request, 'dasher_admin/pages/legal/license_list.html', {'licenses': licenses})

@staff_member_required
def legal_license_add(request):
    from dasher_admin.forms import BusinessLicenseForm
    if request.method == 'POST':
        form = BusinessLicenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã lưu thông tin ĐKKD.')
            return redirect('dasher_admin:legal_license_list')
    else:
        form = BusinessLicenseForm()
    return render(request, 'dasher_admin/pages/legal/license_form.html', {'form': form})

@staff_member_required
def legal_license_edit(request, pk):
    from legal.models import BusinessLicense
    from dasher_admin.forms import BusinessLicenseForm
    license = get_object_or_404(BusinessLicense, pk=pk)
    if request.method == 'POST':
        form = BusinessLicenseForm(request.POST, instance=license)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thông tin ĐKKD.')
            return redirect('dasher_admin:legal_license_list')
    else:
        form = BusinessLicenseForm(instance=license)
    return render(request, 'dasher_admin/pages/legal/license_form.html', {'form': form, 'license': license})

@staff_member_required
def legal_license_delete(request, pk):
    from legal.models import BusinessLicense
    license = get_object_or_404(BusinessLicense, pk=pk)
    license.delete()
    messages.success(request, 'Đã xóa thông tin ĐKKD.')
    return redirect('dasher_admin:legal_license_list')
