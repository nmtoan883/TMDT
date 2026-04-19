from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField
from django.db.models import CharField, TextField, SlugField, ForeignKey
from .forms import ProductForm, ReviewForm
from .models import Category, Product, Review, Wishlist
from cart.forms import CartAddProductForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ContactForm
from .models import ContactInfo
from django.utils import timezone
SUGGESTION_QUERY_MIN_LEN = 2
SUGGESTION_MAX_RESULTS = 6
SUGGESTION_QUERY_MAX_LEN = 100


def _get_product_searchable_fields():
    """
    Build searchable field list dynamically so suggestion search
    keeps working when Product/related models evolve.
    """
    direct_fields = []
    related_fields = []

    for field in Product._meta.get_fields():
        if not getattr(field, 'concrete', False):
            continue

        # Search all text-like direct fields on Product.
        if isinstance(field, (CharField, TextField, SlugField)):
            direct_fields.append(field.name)
            continue

        # Search text-like columns from FK related models (ex: category.name).
        if isinstance(field, ForeignKey):
            related_model = field.related_model
            related_name = field.name
            for rel_field in related_model._meta.get_fields():
                if not getattr(rel_field, 'concrete', False):
                    continue
                if isinstance(rel_field, (CharField, TextField, SlugField)):
                    related_fields.append(f'{related_name}__{rel_field.name}')

    # Remove duplicates while preserving stable order.
    seen = set()
    all_fields = []
    for name in direct_fields + related_fields:
        if name not in seen:
            seen.add(name)
            all_fields.append(name)
    return all_fields


def _build_dynamic_search_q(query, tokens):
    searchable_fields = _get_product_searchable_fields()
    if not searchable_fields:
        return Q(name__icontains=query)

    combined_q = Q()

    for field_name in searchable_fields:
        combined_q |= Q(**{f'{field_name}__icontains': query})

    for token in tokens:
        for field_name in searchable_fields:
            combined_q |= Q(**{f'{field_name}__icontains': token})

    return combined_q


@require_GET
def search_suggestions(request):
    """Search suggestions with broader matching and relevance ordering."""
    q = (request.GET.get('q') or '').strip()[:SUGGESTION_QUERY_MAX_LEN]

    if len(q) < SUGGESTION_QUERY_MIN_LEN:
        return JsonResponse({'suggestions': []})

    keyword_tokens = [token for token in q.split() if token]
    multi_field_q = _build_dynamic_search_q(q, keyword_tokens)

    products = (
        Product.objects.filter(available=True)
        .filter(multi_field_q)
        .select_related('category')
        .annotate(
            match_score=(
                Case(
                    When(name__istartswith=q, then=Value(100)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(name__icontains=q, then=Value(60)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(brand__icontains=q, then=Value(35)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(category__name__icontains=q, then=Value(25)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(description__icontains=q, then=Value(10)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        )
        .only('id', 'name', 'price', 'image', 'slug', 'brand', 'category__name')
        .order_by('-match_score', 'name')[:SUGGESTION_MAX_RESULTS]
    )

    suggestions = []

    for p in products:
        image_url = request.build_absolute_uri(p.image.url) if p.image else ''

        suggestions.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image': image_url,
            'brand': p.brand or '',
            'category': p.category.name if p.category_id else '',
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


def _get_hotdeal_products(limit=None):
    now = timezone.now()
    queryset = (
        Product.objects.filter(
            available=True,
            is_hotdeal=True,
        )
        .filter(Q(hotdeal_start__isnull=True) | Q(hotdeal_start__lte=now))
        .filter(Q(hotdeal_end__isnull=True) | Q(hotdeal_end__gte=now))
        .select_related('category')
        .order_by('hotdeal_end', '-updated', '-created')
    )
    if limit is not None:
        return queryset[:limit]
    return queryset


def _build_hotdeal_countdown(products):
    if not products:
        return None

    first_end = next((product.hotdeal_end for product in products if product.hotdeal_end), None)
    if not first_end:
        return None

    remaining_seconds = max(int((first_end - timezone.now()).total_seconds()), 0)
    days, remainder = divmod(remaining_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {
        'days': f'{days:02d}',
        'hours': f'{hours:02d}',
        'minutes': f'{minutes:02d}',
        'seconds': f'{seconds:02d}',
        'expires_at': first_end,
    }


def _build_product_list_context(request, base_products, category=None, query=None, sort=None):
    categories = Category.objects.all()
    latest_products = (
        Product.objects.filter(available=True)
        .select_related('category')
        .order_by('-created')[:12]
    )
    top_selling_products = (
        Product.objects.filter(available=True)
        .select_related('category')
        .order_by('-stock', '-created')[:12]
    )
    hotdeal_products = list(_get_hotdeal_products())
    hotdeal_countdown = _build_hotdeal_countdown(hotdeal_products)

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

    return {
        'category': category,
        'categories': categories,
        'products': products,
        'latest_products': latest_products,
        'hotdeal_products': hotdeal_products,
        'hotdeal_countdown': hotdeal_countdown,
        'top_selling_products': top_selling_products,
        'top_selling_columns': [
            top_selling_products[0:3],
            top_selling_products[3:6],
            top_selling_products[6:9],
        ],
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
    }


def product_list(request, category_slug=None):
    category = None
    query = request.GET.get('query')
    sort = request.GET.get('sort')

    # Query directly from DB on every request so homepage reflects admin changes immediately.
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

    context = _build_product_list_context(request, base_products, category=category, query=query, sort=sort)
    return render(request, 'core/product/list.html', context)


def hotdeal_list(request):
    hotdeal_products = list(_get_hotdeal_products(limit=24))
    context = {
        'categories': Category.objects.all(),
        'hotdeal_products': hotdeal_products,
        'hotdeal_countdown': _build_hotdeal_countdown(hotdeal_products),
        'is_hotdeal_page': True,
        'page_title': 'Hot Deal',
    }
    return render(request, 'core/product/list.html', context)


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
            return redirect('shop:contact')
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
