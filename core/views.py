from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Review
from django.db.models import Q
from cart.forms import CartAddProductForm

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
    return render(request, 'core/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews
    })
