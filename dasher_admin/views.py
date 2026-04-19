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
def blog_category_list(request):
    from blog.models import Category
    categories = Category.objects.all()
    return render(request, 'dasher_admin/pages/blog/category_list.html', {'categories': categories})
