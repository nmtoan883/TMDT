from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import ProductForm, ReviewForm
from .models import Category, Product, Review, Wishlist
from cart.forms import CartAddProductForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ContactForm
from .models import ContactInfo
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


from decimal import Decimal, InvalidOperation
from django.db.models import Min, Max, Q

RAM_OPTIONS = ['4GB', '8GB', '16GB']
ROM_OPTIONS = ['128GB', '256GB', '512GB']

def _parse_decimal(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None

def _keyword_q(keyword):
    return Q(name__icontains=keyword) | Q(description__icontains=keyword)

RAM_OPTIONS = ['4GB', '8GB', '16GB']
ROM_OPTIONS = ['128GB', '256GB', '512GB']


def _parse_decimal(value):
    """Parse GET parameter into Decimal; return None if empty/invalid."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def _keyword_q(keyword):
    """Match a keyword in Product name or description."""
    return Q(name__icontains=keyword) | Q(description__icontains=keyword)


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    query = request.GET.get('query')
    sort = request.GET.get('sort')

    base_products = Product.objects.filter(available=True)
    
    if query:
        base_products = base_products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query)
        )

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        base_products = base_products.filter(category=category)

    price_bounds = base_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
    )
    price_min_bound = int(price_bounds.get('min_price') or 0)
    price_max_bound = int(price_bounds.get('max_price') or 0)

    brand_options = list(
        base_products.values_list('brand', flat=True).distinct().order_by('brand')
    )

    selected_brands = request.GET.getlist('brands')
    selected_rams = request.GET.getlist('rams')
    selected_roms = request.GET.getlist('roms')

    min_price_param = request.GET.get('min_price')
    max_price_param = request.GET.get('max_price')

    price_min_filter = _parse_decimal(min_price_param) if 'min_price' in request.GET else None
    price_max_filter = _parse_decimal(max_price_param) if 'max_price' in request.GET else None

    min_price_display = int(price_min_filter) if price_min_filter is not None else price_min_bound
    max_price_display = int(price_max_filter) if price_max_filter is not None else price_max_bound

    min_price_display = max(price_min_bound, min_price_display)
    max_price_display = min(price_max_bound, max_price_display)

    if min_price_display > max_price_display:
        max_price_display = min_price_display
        if price_min_filter is not None:
            price_max_filter = price_min_filter

    products = base_products
    filter_q = Q()

    if price_min_filter is not None:
        filter_q &= Q(price__gte=price_min_filter)
    if price_max_filter is not None:
        filter_q &= Q(price__lte=price_max_filter)

    if selected_brands:
        filter_q &= Q(brand__in=selected_brands)

    if selected_rams:
        ram_q = Q()
        for token in selected_rams:
            ram_q |= _keyword_q(token)
        filter_q &= ram_q

    if selected_roms:
        rom_q = Q()
        for token in selected_roms:
            rom_q |= _keyword_q(token)
        filter_q &= rom_q

    products = products.filter(filter_q)
    products = products.select_related('category')

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')
    
    return render(request, 'core/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
        'sort': sort,
        'price_min_bound': price_min_bound,
        'price_max_bound': price_max_bound,
        'min_price': min_price_display,
        'max_price': max_price_display,
        'brand_options': brand_options,
        'brands_selected': selected_brands,
        'ram_options': RAM_OPTIONS,
        'rams_selected': selected_rams,
        'rom_options': ROM_OPTIONS,
        'roms_selected': selected_roms,
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    cart_product_form = CartAddProductForm()
    reviews = product.reviews.all()

    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect(product.get_absolute_url())

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
        'review_form': review_form,
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

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gửi liên hệ thành công! Chúng tôi sẽ phản hồi sớm nhất.')
            return redirect('contact')
    else:
        form = ContactForm()

    contact_info = ContactInfo.objects.first()

    return render(request, 'contact.html', {
        'form': form,
        'contact_info': contact_info,
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
