from decimal import Decimal, InvalidOperation

from django.db.models import Min, Max, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product, Review
from cart.forms import CartAddProductForm

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

    # Slider bounds and checkbox options should reflect the current category + query.
    price_bounds = base_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
    )
    price_min_bound = int(price_bounds.get('min_price') or 0)
    price_max_bound = int(price_bounds.get('max_price') or 0)

    brand_options = list(
        base_products.values_list('brand', flat=True).distinct().order_by('brand')
    )

    # --- Read filters from GET ---
    selected_brands = request.GET.getlist('brands')
    selected_rams = request.GET.getlist('rams')
    selected_roms = request.GET.getlist('roms')

    min_price_param = request.GET.get('min_price')
    max_price_param = request.GET.get('max_price')

    price_min_filter = _parse_decimal(min_price_param) if 'min_price' in request.GET else None
    price_max_filter = _parse_decimal(max_price_param) if 'max_price' in request.GET else None

    # Display values: always show something meaningful on the slider.
    min_price_display = int(price_min_filter) if price_min_filter is not None else price_min_bound
    max_price_display = int(price_max_filter) if price_max_filter is not None else price_max_bound

    # Clamp display values to bounds.
    min_price_display = max(price_min_bound, min_price_display)
    max_price_display = min(price_max_bound, max_price_display)

    if min_price_display > max_price_display:
        max_price_display = min_price_display
        # Keep server-side filtering consistent with what the UI will enforce.
        if price_min_filter is not None:
            price_max_filter = price_min_filter

    # --- Apply filters (AND between Price/Brand/RAM/ROM groups) ---
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

    # --- Sort ---
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
    return render(request, 'core/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews
    })
