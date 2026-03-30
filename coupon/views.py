from django.shortcuts import redirect
from django.contrib import messages
from .models import Coupon
from .forms import CouponApplyForm

def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                coupon = Coupon.objects.get(code__iexact=code, active=True)
                request.session['coupon_id'] = coupon.id
                messages.success(request, "Áp dụng mã thành công!")
            except Coupon.DoesNotExist:
                request.session['coupon_id'] = None
                messages.error(request, "Mã không hợp lệ!")

    return redirect('cart:cart_detail')


def remove_coupon(request):
    request.session['coupon_id'] = None
    messages.success(request, "Đã xóa mã giảm giá.")
    return redirect('cart:cart_detail')