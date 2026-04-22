from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def staff_member_required(view_func=None, redirect_field_name='next', login_url='admin:login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

# Ensure only staff (Admins) can see dashboard
@staff_member_required
def index(request):
    return redirect('admin:dashboard')

@staff_member_required
def blog_list(request):
    from blog.models import Post
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'admin/pages/blog/list.html', {'posts': posts})

@staff_member_required
def blog_add(request):
    from admin.forms import PostForm
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo bài viết thành công.')
            return redirect('admin:blog_list')
    else:
        form = PostForm()
    return render(request, 'admin/pages/blog/post_form.html', {'form': form})

@staff_member_required
def blog_edit(request, pk):
    from blog.models import Post
    from admin.forms import PostForm
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật bài viết thành công.')
            return redirect('admin:blog_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'admin/pages/blog/post_form.html', {'form': form, 'post': post})

@staff_member_required
def blog_delete(request, pk):
    from blog.models import Post
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, 'Đã xóa bài viết.')
    return redirect('admin:blog_list')

@staff_member_required
def blog_category_list(request):
    from blog.models import Category
    categories = Category.objects.all()
    return render(request, 'admin/pages/blog/category_list.html', {'categories': categories})

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
        return redirect('admin:blog_category_list')
    return render(request, 'admin/pages/blog/category_form.html')

@staff_member_required
def blog_category_edit(request, pk):
    from blog.models import Category
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.save()
        messages.success(request, 'Đã cập nhật danh mục thành công.')
        return redirect('admin:blog_category_list')
    return render(request, 'admin/pages/blog/category_form.html', {'category': category})

@staff_member_required
def blog_category_delete(request, pk):
    from blog.models import Category
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Đã xóa danh mục.')
    return redirect('admin:blog_category_list')

@staff_member_required
def account_list(request):
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/pages/accounts/list.html', {'users': users})

@staff_member_required
def account_add(request):
    from admin.forms import UserForm, CustomerProfileForm
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
            return redirect('admin:account_list')
    else:
        user_form = UserForm()
        profile_form = CustomerProfileForm()
    return render(request, 'admin/pages/accounts/form.html', {'user_form': user_form, 'profile_form': profile_form})

@staff_member_required
def account_edit(request, pk):
    from django.contrib.auth.models import User
    from admin.forms import UserForm, CustomerProfileForm
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
            return redirect('admin:account_list')
    else:
        user_form = UserForm(instance=user)
        profile_form = CustomerProfileForm(instance=user.customer_profile)
    return render(request, 'admin/pages/accounts/form.html', {'user_form': user_form, 'profile_form': profile_form, 'account': user})

@staff_member_required
def account_delete(request, pk):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser:
        user.delete()
        messages.success(request, 'Đã xóa tài khoản.')
    else:
        messages.error(request, 'Không thể xóa tài khoản Quản trị viên tối cao.')
    return redirect('admin:account_list')

# Legal Policies
@staff_member_required
def legal_policy_list(request):
    from legal.models import PolicyPage
    policies = PolicyPage.objects.all().order_by('policy_type')
    return render(request, 'admin/pages/legal/policy_list.html', {'policies': policies})

@staff_member_required
def legal_policy_add(request):
    from admin.forms import PolicyPageForm
    if request.method == 'POST':
        form = PolicyPageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo sách sách thành công.')
            return redirect('admin:legal_policy_list')
    else:
        form = PolicyPageForm()
    return render(request, 'admin/pages/legal/policy_form.html', {'form': form})

@staff_member_required
def legal_policy_edit(request, pk):
    from legal.models import PolicyPage
    from admin.forms import PolicyPageForm
    policy = get_object_or_404(PolicyPage, pk=pk)
    if request.method == 'POST':
        form = PolicyPageForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật chính sách thành công.')
            return redirect('admin:legal_policy_list')
    else:
        form = PolicyPageForm(instance=policy)
    return render(request, 'admin/pages/legal/policy_form.html', {'form': form, 'policy': policy})

@staff_member_required
def legal_policy_delete(request, pk):
    from legal.models import PolicyPage
    policy = get_object_or_404(PolicyPage, pk=pk)
    policy.delete()
    messages.success(request, 'Đã xóa chính sách.')
    return redirect('admin:legal_policy_list')

# Legal Licenses
@staff_member_required
def legal_license_list(request):
    from legal.models import BusinessLicense
    licenses = BusinessLicense.objects.all()
    return render(request, 'admin/pages/legal/license_list.html', {'licenses': licenses})

@staff_member_required
def legal_license_add(request):
    from admin.forms import BusinessLicenseForm
    if request.method == 'POST':
        form = BusinessLicenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã lưu thông tin ĐKKD.')
            return redirect('admin:legal_license_list')
    else:
        form = BusinessLicenseForm()
    return render(request, 'admin/pages/legal/license_form.html', {'form': form})

@staff_member_required
def legal_license_edit(request, pk):
    from legal.models import BusinessLicense
    from admin.forms import BusinessLicenseForm
    license = get_object_or_404(BusinessLicense, pk=pk)
    if request.method == 'POST':
        form = BusinessLicenseForm(request.POST, instance=license)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thông tin ĐKKD.')
            return redirect('admin:legal_license_list')
    else:
        form = BusinessLicenseForm(instance=license)
    return render(request, 'admin/pages/legal/license_form.html', {'form': form, 'license': license})

@staff_member_required
def legal_license_delete(request, pk):
    from legal.models import BusinessLicense
    license = get_object_or_404(BusinessLicense, pk=pk)
    license.delete()
    messages.success(request, 'Đã xóa thông tin ĐKKD.')
    return redirect('admin:legal_license_list')

from django.forms import modelform_factory
from core import models as core_models


@staff_member_required
def ec_category_list(request):
    items = core_models.Category.objects.all()
    return render(request, 'admin/pages/ecommerce/category_list.html', {'items': items})

@staff_member_required
def ec_category_add(request):
    FormClass = modelform_factory(core_models.Category, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_category_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/category_form.html', {'form': form})

@staff_member_required
def ec_category_edit(request, pk):
    obj = get_object_or_404(core_models.Category, pk=pk)
    FormClass = modelform_factory(core_models.Category, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_category_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/category_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_category_delete(request, pk):
    obj = get_object_or_404(core_models.Category, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_category_list')

@staff_member_required
def ec_contactinfo_list(request):
    items = core_models.ContactInfo.objects.all()
    return render(request, 'admin/pages/ecommerce/contactinfo_list.html', {'items': items})

@staff_member_required
def ec_contactinfo_add(request):
    FormClass = modelform_factory(core_models.ContactInfo, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_contactinfo_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/contactinfo_form.html', {'form': form})

@staff_member_required
def ec_contactinfo_edit(request, pk):
    obj = get_object_or_404(core_models.ContactInfo, pk=pk)
    FormClass = modelform_factory(core_models.ContactInfo, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_contactinfo_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/contactinfo_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_contactinfo_delete(request, pk):
    obj = get_object_or_404(core_models.ContactInfo, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_contactinfo_list')

@staff_member_required
def ec_policy_list(request):
    items = core_models.Policy.objects.all()
    return render(request, 'admin/pages/ecommerce/policy_list.html', {'items': items})

@staff_member_required
def ec_policy_add(request):
    FormClass = modelform_factory(core_models.Policy, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_policy_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/policy_form.html', {'form': form})

@staff_member_required
def ec_policy_edit(request, pk):
    obj = get_object_or_404(core_models.Policy, pk=pk)
    FormClass = modelform_factory(core_models.Policy, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_policy_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/policy_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_policy_delete(request, pk):
    obj = get_object_or_404(core_models.Policy, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_policy_list')

@staff_member_required
def ec_product_list(request):
    items = core_models.Product.objects.select_related('category').order_by('-updated', '-created')
    return render(request, 'admin/pages/ecommerce/product_list.html', {'items': items})

@staff_member_required
def ec_product_add(request):
    from admin.forms import ProductAdminForm
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_product_list')
    else:
        form = ProductAdminForm()
    return render(request, 'admin/pages/ecommerce/product_form.html', {'form': form})

@staff_member_required
def ec_product_edit(request, pk):
    from admin.forms import ProductAdminForm
    obj = get_object_or_404(core_models.Product, pk=pk)
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_product_list')
    else:
        form = ProductAdminForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/product_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_product_delete(request, pk):
    obj = get_object_or_404(core_models.Product, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_product_list')

@staff_member_required
def ec_hotdeal_campaign_list(request):
    items = core_models.HotDealCampaign.objects.prefetch_related('products').order_by('priority', 'start_at', '-created')
    return render(request, 'admin/pages/ecommerce/hotdeal_campaign_list.html', {'items': items})


@staff_member_required
def ec_hotdeal_campaign_add(request):
    from admin.forms import HotDealCampaignAdminForm

    if request.method == 'POST':
        form = HotDealCampaignAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Hot Deal thành công.')
            return redirect('admin:ec_hotdeal_campaign_list')
    else:
        form = HotDealCampaignAdminForm()
    return render(request, 'admin/pages/ecommerce/hotdeal_campaign_form.html', {'form': form})


@staff_member_required
def ec_hotdeal_campaign_edit(request, pk):
    from admin.forms import HotDealCampaignAdminForm

    obj = get_object_or_404(core_models.HotDealCampaign, pk=pk)
    if request.method == 'POST':
        form = HotDealCampaignAdminForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Hot Deal thành công.')
            return redirect('admin:ec_hotdeal_campaign_list')
    else:
        form = HotDealCampaignAdminForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/hotdeal_campaign_form.html', {'form': form, 'obj': obj})


@staff_member_required
def ec_hotdeal_campaign_delete(request, pk):
    obj = get_object_or_404(core_models.HotDealCampaign, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa Hot Deal.')
    return redirect('admin:ec_hotdeal_campaign_list')

@staff_member_required
def ec_review_list(request):
    items = core_models.Review.objects.all()
    return render(request, 'admin/pages/ecommerce/review_list.html', {'items': items})

@staff_member_required
def ec_review_add(request):
    FormClass = modelform_factory(core_models.Review, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_review_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/review_form.html', {'form': form})

@staff_member_required
def ec_review_edit(request, pk):
    obj = get_object_or_404(core_models.Review, pk=pk)
    FormClass = modelform_factory(core_models.Review, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_review_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/review_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_review_delete(request, pk):
    obj = get_object_or_404(core_models.Review, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_review_list')

@staff_member_required
def ec_contactmessage_list(request):
    items = core_models.ContactMessage.objects.all()
    return render(request, 'admin/pages/ecommerce/contactmessage_list.html', {'items': items})

@staff_member_required
def ec_contactmessage_add(request):
    FormClass = modelform_factory(core_models.ContactMessage, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_contactmessage_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/contactmessage_form.html', {'form': form})

@staff_member_required
def ec_contactmessage_edit(request, pk):
    obj = get_object_or_404(core_models.ContactMessage, pk=pk)
    FormClass = modelform_factory(core_models.ContactMessage, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_contactmessage_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/contactmessage_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_contactmessage_delete(request, pk):
    obj = get_object_or_404(core_models.ContactMessage, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_contactmessage_list')

@staff_member_required
def ec_wishlist_list(request):
    items = core_models.Wishlist.objects.all()
    return render(request, 'admin/pages/ecommerce/wishlist_list.html', {'items': items})

@staff_member_required
def ec_wishlist_add(request):
    FormClass = modelform_factory(core_models.Wishlist, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_wishlist_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/wishlist_form.html', {'form': form})

@staff_member_required
def ec_wishlist_edit(request, pk):
    obj = get_object_or_404(core_models.Wishlist, pk=pk)
    FormClass = modelform_factory(core_models.Wishlist, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_wishlist_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/wishlist_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_wishlist_delete(request, pk):
    obj = get_object_or_404(core_models.Wishlist, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_wishlist_list')



@staff_member_required
def ec_order_list(request):
    from orders.models import Order
    from django.db.models import Q
    items = (
        Order.objects.all()
        .filter(Q(paid=True) | Q(payment_method=Order.PAYMENT_COD))
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'admin/pages/ecommerce/order_list.html', {'items': items})

@staff_member_required
def ec_order_add(request):
    from orders.models import Order
    FormClass = modelform_factory(Order, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_order_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/order_form.html', {'form': form})

@staff_member_required
def ec_order_edit(request, pk):
    from orders.models import Order
    from django.urls import reverse
    obj = get_object_or_404(Order, pk=pk)

    steps = [
        (Order.STATUS_PENDING, 'Đặt hàng', 'bi bi-qr-code'),
        (Order.STATUS_CONFIRMED, 'Chờ xác nhận', 'bi bi-check-circle'),
        (Order.STATUS_PREPARING, 'Chờ lấy hàng', 'bi bi-archive'),
        (Order.STATUS_SHIPPING, 'Đang giao', 'bi bi-truck'),
        (Order.STATUS_COMPLETED, 'Đã giao', 'bi bi-house-check'),
    ]
    status_order = [s for s, _, _ in steps]
    current_idx = status_order.index(obj.status) if obj.status in status_order else 0
    completed_steps = status_order[:current_idx]

    action_buttons = []
    payment_notice = ''
    is_cod = obj.payment_method == Order.PAYMENT_COD
    can_confirm_order = obj.paid or is_cod
    if obj.status == Order.STATUS_PENDING:
        if can_confirm_order:
            action_buttons = [
                ('Xác nhận đơn hàng', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_CONFIRMED]), '#9b59b6'),
                ('Từ chối / Huỷ', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_CANCELLED]), '#d9534f'),
            ]
        else:
            payment_notice = 'Đơn hàng chưa thanh toán nên chưa thể xác nhận. Hãy chờ hệ thống cập nhật thanh toán hoặc kiểm tra thủ công trước.'
    elif obj.status in [Order.STATUS_CONFIRMED, Order.STATUS_PROCESSING]:
        action_buttons = [
            ('Xác nhận đơn hàng', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_PREPARING]), '#e67e22'),
            ('Từ chối / Huỷ', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_CANCELLED]), '#d9534f'),
        ]
    elif obj.status == Order.STATUS_PREPARING:
        action_buttons = [
            ('Chuyển sang đang giao', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_SHIPPING]), '#3498db'),
            ('Huỷ đơn', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_CANCELLED]), '#d9534f'),
        ]
    elif obj.status == Order.STATUS_SHIPPING:
        action_buttons = [
            ('Đã giao hàng thành công', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_COMPLETED]), '#5cb85c'),
            ('Huỷ đơn', reverse('admin:ec_order_set_status', args=[pk, Order.STATUS_CANCELLED]), '#d9534f'),
        ]

    return render(request, 'admin/pages/ecommerce/order_form.html', {
        'obj': obj,
        'steps': steps,
        'completed_steps': completed_steps,
        'action_buttons': action_buttons,
        'payment_notice': payment_notice,
    })

@staff_member_required
def ec_order_delete(request, pk):
    from orders.models import Order
    obj = get_object_or_404(Order, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_order_list')

@staff_member_required
def ec_order_set_status(request, pk, new_status):
    from orders.models import Order
    from orders.services import deduct_stock_for_completed_order
    from coupon.services import create_reward_coupon_for_order
    from core.notifications import create_order_status_notification, create_reward_coupon_notification
    from django.core.exceptions import ValidationError
    obj = get_object_or_404(Order, pk=pk)
    allowed = [s for s, _ in Order.STATUS_CHOICES]
    if new_status in allowed:
        old_status = obj.status
        if new_status in [Order.STATUS_CONFIRMED, Order.STATUS_PREPARING] and not obj.paid and obj.payment_method != Order.PAYMENT_COD:
            messages.error(request, 'Đơn hàng chưa thanh toán nên chưa thể xác nhận.')
            return redirect('admin:ec_order_edit', pk=pk)
        if new_status == Order.STATUS_COMPLETED:
            try:
                deduct_stock_for_completed_order(obj)
            except ValidationError as exc:
                messages.error(request, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
                return redirect('admin:ec_order_edit', pk=pk)
        obj.status = new_status
        if new_status == Order.STATUS_COMPLETED and obj.payment_method == Order.PAYMENT_COD:
            obj.paid = True
        obj.save()
        if old_status != new_status:
            create_order_status_notification(obj, new_status)
            if new_status == Order.STATUS_COMPLETED:
                reward_coupon = create_reward_coupon_for_order(obj)
                create_reward_coupon_notification(obj, reward_coupon)
        messages.success(request, f'Đơn hàng #{pk} → {obj.get_status_display()}')
    else:
        messages.error(request, 'Trạng thái không hợp lệ.')
    return redirect('admin:ec_order_edit', pk=pk)

@staff_member_required
def ec_coupon_list(request):
    from django.core.paginator import Paginator
    from coupon.models import Coupon
    items = (
        Coupon.objects
        .select_related('assigned_user', 'claimed_from')
        .prefetch_related('claimed_coupons__assigned_user')
        .all()
        .order_by('-valid_from', '-id')
    )
    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin/pages/ecommerce/coupon_list.html', {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
    })

@staff_member_required
def ec_coupon_add(request):
    from coupon.models import Coupon
    from admin.forms import CouponAdminForm
    if request.method == 'POST':
        form = CouponAdminForm(request.POST, request.FILES)
        if form.is_valid():
            coupons = form.save_many()
            messages.success(request, f'Đã tạo {len(coupons)} mã giảm giá thành công.')
            return redirect('admin:ec_coupon_list')
    else:
        form = CouponAdminForm()
    return render(request, 'admin/pages/ecommerce/coupon_form.html', {'form': form})

@staff_member_required
def ec_coupon_edit(request, pk):
    from coupon.models import Coupon
    from admin.forms import CouponAdminForm
    obj = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponAdminForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật mã giảm giá.')
            return redirect('admin:ec_coupon_list')
    else:
        form = CouponAdminForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/coupon_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_coupon_push_public(request, pk):
    from django.utils import timezone
    from coupon.models import Coupon

    if request.method != 'POST':
        return redirect('admin:ec_coupon_list')

    obj = get_object_or_404(Coupon, pk=pk)
    if obj.assigned_user_id or obj.claimed_from_id or obj.claimed_coupons.exists():
        messages.error(request, 'Mã này đã thuộc về user hoặc đã được claim, không thể đẩy lên kho chung.')
        return redirect('admin:ec_coupon_list')

    if not obj.active or not obj.claimable:
        messages.error(request, 'Chỉ có thể đẩy mã công khai đang bật lên kho chung.')
        return redirect('admin:ec_coupon_list')

    if obj.public_batch_date and obj.public_batch_slot:
        messages.info(request, 'Mã này đã được đẩy lên kho chung trước đó.')
        return redirect('admin:ec_coupon_list')

    obj.public_batch_date = timezone.localdate()
    obj.public_batch_slot = 'manual'
    obj.save(update_fields=['public_batch_date', 'public_batch_slot'])
    messages.success(request, f'Đã đẩy mã {obj.code} lên kho voucher chung.')
    return redirect('admin:ec_coupon_list')


@staff_member_required
def ec_coupon_delete(request, pk):
    from coupon.models import Coupon
    obj = get_object_or_404(Coupon, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_coupon_list')

@staff_member_required
def ec_promotion_list(request):
    from promotions.models import Promotion
    items = Promotion.objects.all()
    return render(request, 'admin/pages/ecommerce/promotion_list.html', {'items': items})

@staff_member_required
def ec_promotion_add(request):
    from promotions.models import Promotion
    FormClass = modelform_factory(Promotion, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('admin:ec_promotion_list')
    else:
        form = FormClass()
    return render(request, 'admin/pages/ecommerce/promotion_form.html', {'form': form})

@staff_member_required
def ec_promotion_edit(request, pk):
    from promotions.models import Promotion
    obj = get_object_or_404(Promotion, pk=pk)
    FormClass = modelform_factory(Promotion, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('admin:ec_promotion_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'admin/pages/ecommerce/promotion_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_promotion_delete(request, pk):
    from promotions.models import Promotion
    obj = get_object_or_404(Promotion, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('admin:ec_promotion_list')


# -------------------------------------------------------------------------------------------------
# SOCIALACCOUNT / SOCIALAPP CRUD (allauth)
# -------------------------------------------------------------------------------------------------
from allauth.socialaccount.models import SocialApp, SocialAccount
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from django.conf import settings
SocialAppForm = modelform_factory(SocialApp, exclude=['sites'])
SocialAccountForm = modelform_factory(SocialAccount, fields='__all__')

@staff_member_required
def socialapp_list(request):
    objects = SocialApp.objects.all()
    rows = [{'id': obj.id, 'columns': [obj.id, obj.provider, obj.name, obj.client_id]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Social App (OAuth)', 'headers': ['ID', 'Provider', 'Name', 'Client ID'],
        'rows': rows, 'create_url': '/admin/socialapp/create/',
        'update_url_name': 'admin:socialapp_update', 'delete_url_name': 'admin:socialapp_delete'
    })

@staff_member_required
def socialapp_create(request):
    if request.method == 'POST':
        form = SocialAppForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save()
            app.sites.add(settings.SITE_ID)
            messages.success(request, 'Đã tạo Social App.')
            return redirect('admin:socialapp_list')
    else:
        form = SocialAppForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Social App', 'cancel_url': '/admin/socialapp/'})

@staff_member_required
def socialapp_update(request, pk):
    obj = get_object_or_404(SocialApp, pk=pk)
    if request.method == 'POST':
        form = SocialAppForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Social App.')
            return redirect('admin:socialapp_list')
    else:
        form = SocialAppForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Social App', 'cancel_url': '/admin/socialapp/'})

@staff_member_required
def socialapp_delete(request, pk):
    obj = get_object_or_404(SocialApp, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá Social App.')
        return redirect('admin:socialapp_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Social App', 'cancel_url': '/admin/socialapp/'})

@staff_member_required
def socialaccount_list(request):
    objects = SocialAccount.objects.all()
    rows = [{'id': obj.id, 'columns': [obj.id, str(obj.user), obj.provider, obj.uid]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Social Account', 'headers': ['ID', 'User', 'Provider', 'UID'],
        'rows': rows, 'create_url': '/admin/socialaccount/create/',
        'update_url_name': 'admin:socialaccount_update', 'delete_url_name': 'admin:socialaccount_delete'
    })

@staff_member_required
def socialaccount_create(request):
    if request.method == 'POST':
        form = SocialAccountForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Social Account.')
            return redirect('admin:socialaccount_list')
    else:
        form = SocialAccountForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Social Account', 'cancel_url': '/admin/socialaccount/'})

@staff_member_required
def socialaccount_update(request, pk):
    obj = get_object_or_404(SocialAccount, pk=pk)
    if request.method == 'POST':
        form = SocialAccountForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Social Account.')
            return redirect('admin:socialaccount_list')
    else:
        form = SocialAccountForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Social Account', 'cancel_url': '/admin/socialaccount/'})

@staff_member_required
def socialaccount_delete(request, pk):
    obj = get_object_or_404(SocialAccount, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá Social Account.')
        return redirect('admin:socialaccount_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Social Account', 'cancel_url': '/admin/socialaccount/'})


# -------------------------------------------------------------------------------------------------
# CORE DJANGO & SYSTEM CRUD (auth, sites, allauth.account, core.livechatsession)
# -------------------------------------------------------------------------------------------------
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress
from core.models import LiveChatSession

GroupForm = modelform_factory(Group, fields='__all__')
SiteForm = modelform_factory(Site, fields='__all__')
EmailAddressForm = modelform_factory(EmailAddress, fields='__all__')
LiveChatSessionForm = modelform_factory(LiveChatSession, fields='__all__')

# --- USERS ---
@staff_member_required
def core_user_list(request):
    objects = User.objects.all().order_by('-date_joined')
    rows = [{'id': obj.id, 'columns': [obj.id, obj.username, obj.email, obj.is_staff, obj.is_active]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Hệ thống - User', 'headers': ['ID', 'Username', 'Email', 'Staff+', 'Active'],
        'rows': rows, 'create_url': '/admin/sys-user/create/',
        'update_url_name': 'admin:core_user_update', 'delete_url_name': 'admin:core_user_delete'
    })

@staff_member_required
def core_user_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo User.')
            return redirect('admin:core_user_list')
    else:
        form = UserCreationForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Hệ thống - User', 'cancel_url': '/admin/sys-user/'})

@staff_member_required
def core_user_update(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật User.')
            return redirect('admin:core_user_list')
    else:
        form = UserChangeForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Hệ thống - User', 'cancel_url': '/admin/sys-user/'})

@staff_member_required
def core_user_delete(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá User.')
        return redirect('admin:core_user_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Hệ thống - User', 'cancel_url': '/admin/sys-user/'})

# --- GROUPS ---
@staff_member_required
def core_group_list(request):
    objects = Group.objects.all()
    rows = [{'id': obj.id, 'columns': [obj.id, obj.name]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Hệ thống - Group (Role)', 'headers': ['ID', 'Tên Nhóm'],
        'rows': rows, 'create_url': '/admin/sys-group/create/',
        'update_url_name': 'admin:core_group_update', 'delete_url_name': 'admin:core_group_delete'
    })

@staff_member_required
def core_group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Group.')
            return redirect('admin:core_group_list')
    else:
        form = GroupForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Hệ thống - Group', 'cancel_url': '/admin/sys-group/'})

@staff_member_required
def core_group_update(request, pk):
    obj = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Group.')
            return redirect('admin:core_group_list')
    else:
        form = GroupForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Hệ thống - Group', 'cancel_url': '/admin/sys-group/'})

@staff_member_required
def core_group_delete(request, pk):
    obj = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá Group.')
        return redirect('admin:core_group_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Hệ thống - Group', 'cancel_url': '/admin/sys-group/'})

# --- SITES ---
@staff_member_required
def core_site_list(request):
    objects = Site.objects.all()
    rows = [{'id': obj.id, 'columns': [obj.id, obj.domain, obj.name]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Django Sites', 'headers': ['ID', 'Domain', 'Name'],
        'rows': rows, 'create_url': '/admin/sys-site/create/',
        'update_url_name': 'admin:core_site_update', 'delete_url_name': 'admin:core_site_delete'
    })

@staff_member_required
def core_site_create(request):
    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Site.')
            return redirect('admin:core_site_list')
    else:
        form = SiteForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Django Site', 'cancel_url': '/admin/sys-site/'})

@staff_member_required
def core_site_update(request, pk):
    obj = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Site.')
            return redirect('admin:core_site_list')
    else:
        form = SiteForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Django Site', 'cancel_url': '/admin/sys-site/'})

@staff_member_required
def core_site_delete(request, pk):
    obj = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá Site.')
        return redirect('admin:core_site_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Django Site', 'cancel_url': '/admin/sys-site/'})

# --- EMAIL ADDRESSES ---
@staff_member_required
def core_email_list(request):
    objects = EmailAddress.objects.all()
    rows = [{'id': obj.id, 'columns': [obj.id, str(obj.user), obj.email, obj.verified, obj.primary]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Allauth Email Address', 'headers': ['ID', 'User', 'Email', 'Verified?', 'Primary?'],
        'rows': rows, 'create_url': '/admin/sys-email/create/',
        'update_url_name': 'admin:core_email_update', 'delete_url_name': 'admin:core_email_delete'
    })

@staff_member_required
def core_email_create(request):
    if request.method == 'POST':
        form = EmailAddressForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Email.')
            return redirect('admin:core_email_list')
    else:
        form = EmailAddressForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Email Address', 'cancel_url': '/admin/sys-email/'})

@staff_member_required
def core_email_update(request, pk):
    obj = get_object_or_404(EmailAddress, pk=pk)
    if request.method == 'POST':
        form = EmailAddressForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Email.')
            return redirect('admin:core_email_list')
    else:
        form = EmailAddressForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Email Address', 'cancel_url': '/admin/sys-email/'})

@staff_member_required
def core_email_delete(request, pk):
    obj = get_object_or_404(EmailAddress, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá Email.')
        return redirect('admin:core_email_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Email Address', 'cancel_url': '/admin/sys-email/'})

# --- LIVECHAT SESSION ---
@staff_member_required
def core_chat_list(request):
    objects = LiveChatSession.objects.all()
    rows = [{'id': obj.id, 'columns': [obj.id, str(obj.user) if obj.user else obj.session_key, not obj.is_closed, obj.created_at]} for obj in objects]
    return render(request, 'admin/pages/ecommerce/generic_list.html', {
        'model_name': 'Live Chat Session', 'headers': ['ID', 'User/Guest', 'Active?', 'Created'],
        'rows': rows, 'create_url': '/admin/sys-chat/create/',
        'update_url_name': 'admin:core_chat_update', 'delete_url_name': 'admin:core_chat_delete'
    })

@staff_member_required
def core_chat_create(request):
    if request.method == 'POST':
        form = LiveChatSessionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Chat.')
            return redirect('admin:core_chat_list')
    else:
        form = LiveChatSessionForm()
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Live Chat', 'cancel_url': '/admin/sys-chat/'})

@staff_member_required
def core_chat_update(request, pk):
    obj = get_object_or_404(LiveChatSession, pk=pk)
    if request.method == 'POST':
        form = LiveChatSessionForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Chat.')
            return redirect('admin:core_chat_list')
    else:
        form = LiveChatSessionForm(instance=obj)
    return render(request, 'admin/pages/ecommerce/generic_form.html', {'form': form, 'model_name': 'Live Chat', 'cancel_url': '/admin/sys-chat/'})

@staff_member_required
def core_chat_delete(request, pk):
    obj = get_object_or_404(LiveChatSession, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Đã xoá Chat.')
        return redirect('admin:core_chat_list')
    return render(request, 'admin/pages/ecommerce/generic_confirm_delete.html', {'object': obj, 'model_name': 'Live Chat', 'cancel_url': '/admin/sys-chat/'})

from django.contrib.auth import logout as auth_logout
def admin_logout(request):
    auth_logout(request)
    return redirect("/")

@staff_member_required
def ec_banner_list(request):
    from core.models import Banner
    banners = Banner.objects.all()
    return render(request, 'admin/pages/ecommerce/banner_list.html', {'banners': banners})

@staff_member_required
def ec_banner_add(request):
    from admin.forms import BannerForm
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm Banner thành công.')
            return redirect('admin:ec_banner_list')
    else:
        form = BannerForm()
    return render(request, 'admin/pages/ecommerce/banner_form.html', {'form': form, 'title': 'Thêm Banner mới'})

@staff_member_required
def ec_banner_edit(request, pk):
    from core.models import Banner
    from admin.forms import BannerForm
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật Banner thành công.')
            return redirect('admin:ec_banner_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'admin/pages/ecommerce/banner_form.html', {'form': form, 'banner': banner, 'title': 'Chỉnh sửa Banner'})

@staff_member_required
def ec_banner_delete(request, pk):
    from core.models import Banner
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    messages.success(request, 'Đã xoá Banner thành công.')
    return redirect('admin:ec_banner_list')
# ================= DASHBOARD =================
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
import json

@staff_member_required
def dashboard(request):
    from orders.models import Order, OrderItem
    from django.contrib.auth.models import User
    from core.models import Product

    orders = Order.objects.all()
    completed_orders = orders.filter(status=Order.STATUS_COMPLETED)
    active_orders = orders.filter(
        status__in=[
            Order.STATUS_CONFIRMED,
            Order.STATUS_PREPARING,
            Order.STATUS_SHIPPING,
            Order.STATUS_PROCESSING,
        ]
    )
    admin_visible_orders = orders.filter(paid=True) | orders.filter(payment_method=Order.PAYMENT_COD)

    total_revenue = completed_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = orders.count()
    completed_count = completed_orders.count()
    active_count = active_orders.count()
    cancelled_count = orders.filter(status=Order.STATUS_CANCELLED).count()
    pending_payment_count = orders.filter(status=Order.STATUS_PENDING, payment_method=Order.PAYMENT_SEPAY, paid=False).count()
    pending_confirmation_count = orders.filter(status=Order.STATUS_CONFIRMED).count()
    preparing_count = orders.filter(status=Order.STATUS_PREPARING).count()
    shipping_count = orders.filter(status=Order.STATUS_SHIPPING).count()
    total_customers = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_products = Product.objects.count()
    today = timezone.localdate()
    today_revenue = completed_orders.filter(created_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = (total_revenue / completed_count) if completed_count else 0

    revenue_by_day = (
        completed_orders
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total=Sum('total_amount'))
        .order_by('date')
    )

    labels = [str(i['date']) for i in revenue_by_day]
    data = [float(i['total']) for i in revenue_by_day]
    recent_orders = (
        admin_visible_orders
        .distinct()
        .prefetch_related('items__product')
        .order_by('-created_at')[:8]
    )

    status_counts = {
        row['status']: row['count']
        for row in orders.values('status').annotate(count=Count('id'))
    }
    status_summary = [
        {
            'key': Order.STATUS_PENDING,
            'label': 'Chờ thanh toán',
            'count': status_counts.get(Order.STATUS_PENDING, 0),
            'class': 'warning',
        },
        {
            'key': Order.STATUS_CONFIRMED,
            'label': 'Chờ xác nhận',
            'count': status_counts.get(Order.STATUS_CONFIRMED, 0),
            'class': 'info',
        },
        {
            'key': Order.STATUS_PREPARING,
            'label': 'Chờ lấy hàng',
            'count': status_counts.get(Order.STATUS_PREPARING, 0),
            'class': 'primary',
        },
        {
            'key': Order.STATUS_SHIPPING,
            'label': 'Đang giao',
            'count': status_counts.get(Order.STATUS_SHIPPING, 0),
            'class': 'secondary',
        },
        {
            'key': Order.STATUS_COMPLETED,
            'label': 'Đã giao',
            'count': status_counts.get(Order.STATUS_COMPLETED, 0),
            'class': 'success',
        },
        {
            'key': Order.STATUS_CANCELLED,
            'label': 'Đã huỷ',
            'count': status_counts.get(Order.STATUS_CANCELLED, 0),
            'class': 'danger',
        },
    ]
    top_products = (
        OrderItem.objects.filter(order__status=Order.STATUS_COMPLETED)
        .values('product__name')
        .annotate(quantity=Sum('quantity'), revenue=Sum('price'))
        .order_by('-quantity')[:5]
    )

    context = {
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'avg_order_value': avg_order_value,
        'total_orders': total_orders,
        'completed_count': completed_count,
        'active_count': active_count,
        'cancelled_count': cancelled_count,
        'pending_payment_count': pending_payment_count,
        'pending_confirmation_count': pending_confirmation_count,
        'preparing_count': preparing_count,
        'shipping_count': shipping_count,
        'total_customers': total_customers,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'status_summary': status_summary,
        'top_products': top_products,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }

    return render(request, 'admin/pages/dashboard/dashboard.html', context)
