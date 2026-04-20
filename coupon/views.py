from django.contrib import messages
from django.shortcuts import redirect

from .forms import CouponApplyForm
from .models import Coupon


def apply(request):
    if request.method == "POST":
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                coupon = Coupon.objects.get(code__iexact=code)
            except Coupon.DoesNotExist:
                messages.error(request, "Ma giam gia khong ton tai.")
                return redirect("cart:cart_detail")

            if coupon.is_valid():
                request.session["coupon_id"] = coupon.id
                messages.success(request, f"Ap ma {coupon.code} thanh cong.")
            else:
                messages.error(request, "Ma giam gia da het han hoac chua kich hoat.")

    return redirect("cart:cart_detail")


def remove(request):
    request.session.pop("coupon_id", None)
    messages.success(request, "Da xoa ma giam gia.")
    return redirect("cart:cart_detail")



