from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Post, Category


def blog_list(request):
    posts = Post.objects.filter(is_published=True).select_related('category')
    featured_post = posts.filter(is_featured=True).first()
    latest_posts = posts[:5]
    categories = Category.objects.all()

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_post': featured_post,
        'latest_posts': latest_posts,
        'categories': categories,
        'page_obj': page_obj,
        'page_title': 'Tin tức công nghệ',
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related('category'),
        slug=slug,
        is_published=True
    )

    post.views += 1
    post.save(update_fields=['views'])

    related_posts = Post.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(id=post.id)[:3]

    latest_posts = Post.objects.filter(is_published=True).exclude(id=post.id)[:5]

    context = {
        'post': post,
        'related_posts': related_posts,
        'latest_posts': latest_posts,
        'page_title': post.title,
    }
    return render(request, 'blog/blog_detail.html', context)


def blog_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(is_published=True, category=category).select_related('category')
    categories = Category.objects.all()
    latest_posts = Post.objects.filter(is_published=True)[:5]

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'current_category': category,
        'categories': categories,
        'latest_posts': latest_posts,
        'page_obj': page_obj,
        'featured_post': None,
        'page_title': f'Danh mục: {category.name}',
    }
    return render(request, 'blog/blog_list.html', context)


def blog_search(request):
    query = request.GET.get('q', '').strip()
    posts = Post.objects.filter(is_published=True)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query)
        )

    categories = Category.objects.all()
    latest_posts = Post.objects.filter(is_published=True)[:5]

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'categories': categories,
        'latest_posts': latest_posts,
        'page_obj': page_obj,
        'featured_post': None,
        'page_title': f'Kết quả tìm kiếm: {query}' if query else 'Tìm kiếm bài viết',
    }
    return render(request, 'blog/blog_list.html', context)