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
