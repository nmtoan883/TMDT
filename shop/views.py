from django.shortcuts import render
from coupons.models import Coupon

def home(request):
    return render(request, 'shop/home.html')

def cart(request):
    cart_total = 2940.00
    discount = 0
    final_total = cart_total
    applied_coupon = None

    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.is_valid():
                applied_coupon = coupon.code

                if coupon.discount_percent:
                    discount = cart_total * coupon.discount_percent / 100
                elif coupon.discount_amount:
                    discount = float(coupon.discount_amount)

                final_total = cart_total - discount
        except Coupon.DoesNotExist:
            pass

    context = {
        'cart_total': cart_total,
        'discount': discount,
        'final_total': final_total,
        'applied_coupon': applied_coupon,
    }
    return render(request, 'shop/checkout.html', context)

def contact(request):
    return render(request, 'shop/contact.html')