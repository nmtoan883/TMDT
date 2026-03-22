from django.shortcuts import render, get_object_or_404
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

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, active=True)
    latest_posts = Post.objects.filter(active=True).exclude(id=post.id)[:5]

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'latest_posts': latest_posts,
    })