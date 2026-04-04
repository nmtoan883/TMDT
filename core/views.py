from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Category, Product, Review
from django.db.models import Q
from cart.forms import CartAddProductForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactForm

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
        suggestions.append(
            {
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'image': image_url,
                'url': p.get_absolute_url(),
            }
        )

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
    return render(request, 'core/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews
    })

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gửi liên hệ thành công! Chúng tôi sẽ phản hồi sớm nhất.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
