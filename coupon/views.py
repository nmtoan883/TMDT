from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import Coupon
from .forms import CouponApplyForm
from cart.cart import Cart


def apply_coupon(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = CouponApplyForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                coupon = Coupon.objects.get(code__iexact=code, active=True)
                now = timezone.now()

                if coupon.valid_from > now or coupon.valid_to < now:
                    request.session['coupon_id'] = None
                    messages.error(request, "Mã đã hết hạn hoặc chưa đến thời gian sử dụng!")

                elif cart.get_total_price() < coupon.min_amount:
                    request.session['coupon_id'] = None
                    messages.error(
                        request,
                        f"Đơn hàng phải từ {coupon.min_amount:,.0f}₫ mới dùng được mã này!"
                    )

                else:
                    request.session['coupon_id'] = coupon.id
                    messages.success(request, "Áp dụng mã giảm giá thành công!")

            except Coupon.DoesNotExist:
                request.session['coupon_id'] = None
                messages.error(request, "Mã giảm giá không hợp lệ!")

    return redirect('cart:cart_detail')


def remove_coupon(request):
    request.session['coupon_id'] = None
    messages.success(request, "Đã xóa mã giảm giá!")
    return redirect('cart:cart_detail')