from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Review
from django.db.models import Q
from cart.forms import CartAddProductForm
from django.shortcuts import render, redirect, get_object_or_404
from .wishlist import Wishlist

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
    wishlist = Wishlist(request)
    is_favorite = product.id in wishlist

    recent = request.session.get('recently_viewed', [])

    if product.id in recent:
        recent.remove(product.id)

    recent.insert(0, product.id)
    request.session['recently_viewed'] = recent[:6]

    recent_products = list(Product.objects.filter(id__in=recent, available=True))
    recent_products.sort(key=lambda x: recent.index(x.id))

    return render(request, 'core/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'recent_products': recent_products,
        'wishlist': wishlist,
        'is_favorite': is_favorite,
    })

def wishlist_detail(request):
    wishlist = Wishlist(request)
    products = wishlist.get_products()
    return render(request, 'core/product/wishlist.html', {
        'wishlist_products': products,
    })


def wishlist_add(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    wishlist.add(product.id)
    return redirect(product.get_absolute_url())


def wishlist_remove(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    wishlist.remove(product.id)
    return redirect('shop:wishlist_detail')
