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

from django.forms import modelform_factory
from core import models as core_models


@staff_member_required
def ec_category_list(request):
    items = core_models.Category.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/category_list.html', {'items': items})

@staff_member_required
def ec_category_add(request):
    FormClass = modelform_factory(core_models.Category, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_category_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/category_form.html', {'form': form})

@staff_member_required
def ec_category_edit(request, pk):
    obj = get_object_or_404(core_models.Category, pk=pk)
    FormClass = modelform_factory(core_models.Category, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_category_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/category_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_category_delete(request, pk):
    obj = get_object_or_404(core_models.Category, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_category_list')

@staff_member_required
def ec_contactinfo_list(request):
    items = core_models.ContactInfo.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/contactinfo_list.html', {'items': items})

@staff_member_required
def ec_contactinfo_add(request):
    FormClass = modelform_factory(core_models.ContactInfo, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_contactinfo_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/contactinfo_form.html', {'form': form})

@staff_member_required
def ec_contactinfo_edit(request, pk):
    obj = get_object_or_404(core_models.ContactInfo, pk=pk)
    FormClass = modelform_factory(core_models.ContactInfo, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_contactinfo_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/contactinfo_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_contactinfo_delete(request, pk):
    obj = get_object_or_404(core_models.ContactInfo, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_contactinfo_list')

@staff_member_required
def ec_policy_list(request):
    items = core_models.Policy.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/policy_list.html', {'items': items})

@staff_member_required
def ec_policy_add(request):
    FormClass = modelform_factory(core_models.Policy, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_policy_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/policy_form.html', {'form': form})

@staff_member_required
def ec_policy_edit(request, pk):
    obj = get_object_or_404(core_models.Policy, pk=pk)
    FormClass = modelform_factory(core_models.Policy, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_policy_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/policy_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_policy_delete(request, pk):
    obj = get_object_or_404(core_models.Policy, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_policy_list')

@staff_member_required
def ec_product_list(request):
    items = core_models.Product.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/product_list.html', {'items': items})

@staff_member_required
def ec_product_add(request):
    FormClass = modelform_factory(core_models.Product, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_product_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/product_form.html', {'form': form})

@staff_member_required
def ec_product_edit(request, pk):
    obj = get_object_or_404(core_models.Product, pk=pk)
    FormClass = modelform_factory(core_models.Product, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_product_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/product_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_product_delete(request, pk):
    obj = get_object_or_404(core_models.Product, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_product_list')

@staff_member_required
def ec_review_list(request):
    items = core_models.Review.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/review_list.html', {'items': items})

@staff_member_required
def ec_review_add(request):
    FormClass = modelform_factory(core_models.Review, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_review_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/review_form.html', {'form': form})

@staff_member_required
def ec_review_edit(request, pk):
    obj = get_object_or_404(core_models.Review, pk=pk)
    FormClass = modelform_factory(core_models.Review, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_review_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/review_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_review_delete(request, pk):
    obj = get_object_or_404(core_models.Review, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_review_list')

@staff_member_required
def ec_contactmessage_list(request):
    items = core_models.ContactMessage.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/contactmessage_list.html', {'items': items})

@staff_member_required
def ec_contactmessage_add(request):
    FormClass = modelform_factory(core_models.ContactMessage, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_contactmessage_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/contactmessage_form.html', {'form': form})

@staff_member_required
def ec_contactmessage_edit(request, pk):
    obj = get_object_or_404(core_models.ContactMessage, pk=pk)
    FormClass = modelform_factory(core_models.ContactMessage, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_contactmessage_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/contactmessage_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_contactmessage_delete(request, pk):
    obj = get_object_or_404(core_models.ContactMessage, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_contactmessage_list')

@staff_member_required
def ec_wishlist_list(request):
    items = core_models.Wishlist.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/wishlist_list.html', {'items': items})

@staff_member_required
def ec_wishlist_add(request):
    FormClass = modelform_factory(core_models.Wishlist, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_wishlist_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/wishlist_form.html', {'form': form})

@staff_member_required
def ec_wishlist_edit(request, pk):
    obj = get_object_or_404(core_models.Wishlist, pk=pk)
    FormClass = modelform_factory(core_models.Wishlist, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_wishlist_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/wishlist_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_wishlist_delete(request, pk):
    obj = get_object_or_404(core_models.Wishlist, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_wishlist_list')



@staff_member_required
def ec_order_list(request):
    from orders.models import Order
    items = Order.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/order_list.html', {'items': items})

@staff_member_required
def ec_order_add(request):
    from orders.models import Order
    FormClass = modelform_factory(Order, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_order_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/order_form.html', {'form': form})

@staff_member_required
def ec_order_edit(request, pk):
    from orders.models import Order
    obj = get_object_or_404(Order, pk=pk)
    FormClass = modelform_factory(Order, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_order_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/order_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_order_delete(request, pk):
    from orders.models import Order
    obj = get_object_or_404(Order, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_order_list')

@staff_member_required
def ec_coupon_list(request):
    from coupon.models import Coupon
    items = Coupon.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/coupon_list.html', {'items': items})

@staff_member_required
def ec_coupon_add(request):
    from coupon.models import Coupon
    FormClass = modelform_factory(Coupon, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_coupon_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/coupon_form.html', {'form': form})

@staff_member_required
def ec_coupon_edit(request, pk):
    from coupon.models import Coupon
    obj = get_object_or_404(Coupon, pk=pk)
    FormClass = modelform_factory(Coupon, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thành công.')
            return redirect('dasher_admin:ec_coupon_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/coupon_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_coupon_delete(request, pk):
    from coupon.models import Coupon
    obj = get_object_or_404(Coupon, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_coupon_list')

@staff_member_required
def ec_promotion_list(request):
    from promotions.models import Promotion
    items = Promotion.objects.all()
    return render(request, 'dasher_admin/pages/ecommerce/promotion_list.html', {'items': items})

@staff_member_required
def ec_promotion_add(request):
    from promotions.models import Promotion
    FormClass = modelform_factory(Promotion, exclude=[])
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mới thành công.')
            return redirect('dasher_admin:ec_promotion_list')
    else:
        form = FormClass()
    return render(request, 'dasher_admin/pages/ecommerce/promotion_form.html', {'form': form})

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
            return redirect('dasher_admin:ec_promotion_list')
    else:
        form = FormClass(instance=obj)
    return render(request, 'dasher_admin/pages/ecommerce/promotion_form.html', {'form': form, 'obj': obj})

@staff_member_required
def ec_promotion_delete(request, pk):
    from promotions.models import Promotion
    obj = get_object_or_404(Promotion, pk=pk)
    obj.delete()
    messages.success(request, 'Đã xóa đối tượng.')
    return redirect('dasher_admin:ec_promotion_list')
