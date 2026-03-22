from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Category

def post_list(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    posts = Post.objects.filter(active=True)
    categories = Category.objects.all()

    if query:
        posts = posts.filter(title__icontains=query)

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    featured_post = posts.filter(featured=True).first()

    if featured_post:
        posts = posts.exclude(id=featured_post.id)

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {
        'featured_post': featured_post,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    })
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, active=True)

    post.views += 1
    post.save()

    latest_posts = Post.objects.filter(active=True).exclude(id=post.id)[:5]
    related_posts = Post.objects.filter(
        active=True,
        category=post.category
    ).exclude(id=post.id)[:3] if post.category else []

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'latest_posts': latest_posts,
        'related_posts': related_posts,
    })