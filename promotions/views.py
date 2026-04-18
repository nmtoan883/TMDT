from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Promotion


def promotion_list(request):
    now = timezone.now()
    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products')

    featured_promotions = promotions.filter(is_featured=True)[:3]
    latest_promotions = promotions[:12]

    context = {
        'featured_promotions': featured_promotions,
        'promotions': latest_promotions,
    }
    return render(request, 'promotions/promotion_list.html', context)


def promotion_detail(request, slug):
    promotion = get_object_or_404(
        Promotion.objects.prefetch_related('products'),
        slug=slug,
        is_active=True
    )
    related_products = promotion.products.all()[:12]

    context = {
        'promotion': promotion,
        'related_products': related_products,
    }
    return render(request, 'promotions/promotion_detail.html', context)