from django.shortcuts import redirect
from django.contrib import messages
from .forms import CouponApplyForm
from .models import Coupon


def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                coupon = Coupon.objects.get(code__iexact=code)

                if coupon.is_valid():
                    request.session['coupon_id'] = coupon.id
                    messages.success(request, f'Áp mã {coupon.code} thành công.')
                else:
                    messages.error(request, 'Mã giảm giá đã hết hạn hoặc chưa kích hoạt.')
            except Coupon.DoesNotExist:
                messages.error(request, 'Mã giảm giá không tồn tại.')

    return redirect('cart')