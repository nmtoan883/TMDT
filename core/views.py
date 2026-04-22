from django.utils import timezone
from datetime import timedelta
from promotions.models import Promotion
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField, Avg
from django.db.models import CharField, TextField, SlugField, ForeignKey
from .forms import ProductForm, ReviewForm
from .models import Banner, Category, Product, Review, UserNotification, Wishlist
from cart.forms import CartAddProductForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ContactForm
from .models import ContactInfo
from orders.models import OrderItem
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
        .prefetch_related('hotdeal_campaigns')
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
        .only('id', 'name', 'price', 'old_price', 'discount_percent', 'is_hotdeal', 'hotdeal_start', 'hotdeal_end', 'image', 'slug', 'brand', 'category__name')
        .order_by('-match_score', 'name')[:SUGGESTION_MAX_RESULTS]
    )

    suggestions = []

    for p in products:
        image_url = request.build_absolute_uri(p.image.url) if p.image else ''

        suggestions.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.display_price),
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



def _get_hotdeal_products(limit=None):
    now = timezone.now()
    products = list(
        Product.objects.filter(
            Q(
                available=True,
                is_hotdeal=True,
            ) |
            Q(
                available=True,
                hotdeal_campaigns__is_active=True,
                hotdeal_campaigns__start_at__lte=now,
                hotdeal_campaigns__end_at__gte=now,
            )
        )
        .select_related('category')
        .prefetch_related('hotdeal_campaigns')
        .distinct()
    )
    products = [product for product in products if product.is_hotdeal_active]

    products.sort(
        key=lambda product: (
            product.effective_hotdeal_end or timezone.now(),
            -int(product.updated.timestamp()),
            -int(product.created.timestamp()),
        )
    )
    if limit is not None:
        return products[:limit]
    return products


def _build_hotdeal_countdown(products):
    if not products:
        return None

    first_end = next((product.effective_hotdeal_end for product in products if product.effective_hotdeal_end), None)
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


def _apply_display_pricing(products):
    for product in products:
        product.base_price = product.price
        product.base_old_price = product.old_price
        product.base_hotdeal_start = product.hotdeal_start
        product.base_hotdeal_end = product.hotdeal_end
        product.price = product.display_price
        product.old_price = product.display_old_price
        product.hotdeal_start = product.effective_hotdeal_start
        product.hotdeal_end = product.effective_hotdeal_end
        product.discount_percent = product.display_discount_percent
    return products


def _build_product_list_context(request, base_products, category=None, query=None, sort=None):
    categories = Category.objects.all()
    hotdeal_products = _get_hotdeal_products()
    _apply_display_pricing(hotdeal_products)
    hotdeal_countdown = _build_hotdeal_countdown(hotdeal_products)

    now = timezone.now()
    latest_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-is_featured', '-created_at')[:3]

    price_bounds = base_products.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
    )
    price_min_bound = int(price_bounds.get('min_price') or 0)
    price_max_bound = int(price_bounds.get('max_price') or 0)

    brand_options = list(
        base_products.values_list('brand', flat=True).distinct().order_by('brand')
    )

    # Handle both 'brand' (singular) and 'brands' (plural) for compatibility
    selected_brands = request.GET.getlist('brands') or request.GET.getlist('brand')
    selected_categories = request.GET.getlist('category')
    selected_rams = request.GET.getlist('rams')
    selected_roms = request.GET.getlist('roms')
    
    # Handle special filters
    selected_sale = request.GET.get('sale')
    selected_new = request.GET.get('new')
    selected_hot = request.GET.get('hot')
    selected_rating = request.GET.get('rating')

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
    
    if selected_categories:
        filter_q &= Q(category__id__in=selected_categories)

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
    
    # Handle special filters
    if selected_sale:
        filter_q &= Q(old_price__isnull=False)  # Products with old price are on sale
    
    if selected_new:
        # Products created in the last 30 days are considered new
        thirty_days_ago = timezone.now() - timedelta(days=30)
        filter_q &= Q(created__gte=thirty_days_ago)
    
    if selected_hot:
        filter_q &= Q(is_hotdeal=True)

    if selected_rating:
        try:
            rating_val = int(selected_rating)
            # Annotate products with average rating and filter
            products = products.annotate(avg_rating=Avg('reviews__rating'))
            filter_q &= Q(avg_rating__gte=rating_val)
        except (ValueError, TypeError):
            pass

    products = products.filter(filter_q)
    products = products.select_related('category').prefetch_related('hotdeal_campaigns')

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')

    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    products = list(page_obj.object_list)
    _apply_display_pricing(products)

    home_banners = Banner.objects.filter(is_active=True)

    return {
        'category': category,
        'categories': categories,
        'home_banners': home_banners,
        'products': products,
        'page_obj': page_obj,
        'paginator': paginator,
        'pagination_querystring': pagination_params.urlencode(),
        'hotdeal_products': hotdeal_products,
        'hotdeal_countdown': hotdeal_countdown,
        'latest_promotions': latest_promotions,
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
        'selected_categories': selected_categories,
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
    hotdeal_products = _get_hotdeal_products(limit=24)
    _apply_display_pricing(hotdeal_products)
    now = timezone.now()
    context = {
        'categories': Category.objects.all(),
        'home_banners': Banner.objects.filter(is_active=True),
        'hotdeal_products': hotdeal_products,
        'hotdeal_countdown': _build_hotdeal_countdown(hotdeal_products),
        'latest_promotions': Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-is_featured', '-created_at')[:3],
        'is_hotdeal_page': True,
        'page_title': 'Hot Deal',
    }
    return render(request, 'core/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product.objects.prefetch_related('hotdeal_campaigns'), id=id, slug=slug, available=True)
    _apply_display_pricing([product])

    cart_product_form = CartAddProductForm()
    reviews = product.reviews.all()

    # Check if user has purchased this product
    has_purchased = False
    can_review = False
    review_form = ReviewForm()
    
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            product=product,
            order__user=request.user
        ).exists()
        can_review = has_purchased
    
    if request.method == 'POST' and request.user.is_authenticated and can_review:
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            rating = int(request.POST.get('rating', 0))
            if rating > 0 and rating <= 5:
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.rating = rating
                review.save()
                messages.success(request, 'Cảm ơn bạn! Đánh giá của bạn đã được gửi thành công.')
                return redirect(product.get_absolute_url())
            else:
                review_form.add_error('rating', 'Vui lòng chọn số sao từ 1 đến 5')

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
        'can_review': can_review,
        'has_purchased': has_purchased,
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
    ).select_related('product').prefetch_related('product__hotdeal_campaigns')
    for item in wishlist_items:
        _apply_display_pricing([item.product])

    return render(request, 'core/product/wishlist.html', {
    'wishlist_items': wishlist_items
    })


@login_required
def notification_list(request):
    notifications = UserNotification.objects.filter(user=request.user)
    return render(request, 'core/notifications/list.html', {
        'notifications': notifications,
    })


@login_required
def notification_open(request, pk):
    notification = get_object_or_404(UserNotification, pk=pk, user=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return redirect(notification.action_url or 'shop:notification_list')


@login_required
def notification_api(request):
    notifications = UserNotification.objects.filter(user=request.user)[:5]
    return JsonResponse({
        'unread_count': UserNotification.objects.filter(user=request.user, is_read=False).count(),
        'notifications': [
            {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'url': reverse('shop:notification_open', args=[notification.id]),
            }
            for notification in notifications
        ],
    })


@require_GET
def public_voucher_api(request):
    from accounts.views import (
        _active_public_slots,
        _annotate_public_voucher_groups_for_user,
        _get_daily_public_vouchers,
        _group_public_vouchers,
        _next_public_voucher_slot_label,
    )

    def money_text(value):
        if not value:
            return '0 đ'
        return f'{int(value):,}'.replace(',', '.') + ' đ'

    now = timezone.now()
    voucher_groups = _group_public_vouchers(_get_daily_public_vouchers(request.user, now))
    voucher_groups = _annotate_public_voucher_groups_for_user(voucher_groups, request.user, now)

    return JsonResponse({
        'is_authenticated': request.user.is_authenticated,
        'can_claim': bool(_active_public_slots(now)),
        'next_slot_label': _next_public_voucher_slot_label(now),
        'vouchers': [
            {
                'id': voucher.id,
                'discount_label': f'{voucher.discount_percent}%' if voucher.discount_percent else money_text(voucher.discount_amount),
                'min_order_amount': money_text(voucher.min_order_amount),
                'claim_valid_days': voucher.claim_valid_days,
                'available_count': voucher.available_count,
                'claimed_today': voucher.claimed_today,
            }
            for voucher in voucher_groups
        ],
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


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LiveChatSession, LiveChatMessage

@csrf_exempt
def chat_sync_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'msg': 'Unauthorized'}, status=401)

    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    user = request.user

    # Get or Create Session based ON USER IDENTITY
    chat_session = LiveChatSession.objects.filter(user=user).first()
    if not chat_session:
        chat_session = LiveChatSession.objects.create(user=user)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            if message_content and not chat_session.is_closed:
                LiveChatMessage.objects.create(
                    session=chat_session,
                    content=message_content,
                    is_admin=False
                )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
            
    # GET method - fetch messages
    messages = chat_session.messages.all().order_by('created_at')
    msg_list = []
    
    # We will prepend a default welcome message
    msg_list.append({
        'content': 'Chào bạn! 👋<br>Chúng tôi có thể giúp gì cho bạn hôm nay?',
        'is_admin': True,
        'created_at': chat_session.created_at.isoformat()
    })
    
    for m in messages:
        msg_list.append({
            'content': m.content,
            'is_admin': m.is_admin,
            'created_at': m.created_at.isoformat()
        })
        
    return JsonResponse({'status': 'ok', 'messages': msg_list})
