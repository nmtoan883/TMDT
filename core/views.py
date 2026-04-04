from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import ProductForm
from .models import Category, Product, Review, Wishlist
from cart.forms import CartAddProductForm
from django.views.decorators.http import require_POST
SUGGESTION_QUERY_MIN_LEN = 2
SUGGESTION_MAX_RESULTS = 8
SUGGESTION_QUERY_MAX_LEN = 100


@require_GET
def search_suggestions(request):
    """
    Gợi ý tìm kiếm theo tên sản phẩm (JSON).
    Chỉ đọc các cột cần thiết qua .only() để giảm tải DB.
    """
    q = (request.GET.get('q') or '').strip()[:SUGGESTION_QUERY_MAX_LEN]

    if len(q) < SUGGESTION_QUERY_MIN_LEN:
        return JsonResponse({'suggestions': []})

    products = (
        Product.objects.filter(available=True, name__icontains=q)
        .only('id', 'name', 'price', 'image', 'slug')
        .order_by('name')[:SUGGESTION_MAX_RESULTS]
    )

    suggestions = []

    for p in products:
        image_url = request.build_absolute_uri(p.image.url) if p.image else ''

        suggestions.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image': image_url,
            'url': p.get_absolute_url(),
        })

    return JsonResponse({'suggestions': suggestions})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    query = request.GET.get('query')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query)
        )

    sort = request.GET.get('sort')

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'core/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
        'sort': sort
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    reviews = product.reviews.all()

    is_in_wishlist = False

    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    return render(request, 'core/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
        'is_in_wishlist': is_in_wishlist
    })


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('shop:wishlist_list')


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect('shop:wishlist_list')


@login_required
def wishlist_list(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(request, 'core/product/wishlist.html', {
    'wishlist_items': wishlist_items
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop:product_list')
        else:
            print(form.errors)  # 👈 debug lỗi
    else:
        form = ProductForm()

    return render(request, 'product/create.html', {'form': form})