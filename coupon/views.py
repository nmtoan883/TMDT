from django.contrib import messages
from django.shortcuts import redirect

from cart.cart import Cart
from .forms import CouponApplyForm
from .models import Coupon


def _format_vnd(amount):
    return f"{amount:,.0f}".replace(",", ".")


def apply(request):
    if request.method == "POST":
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                coupon = Coupon.objects.get(code__iexact=code)
            except Coupon.DoesNotExist:
                messages.error(request, "Mã giảm giá không tồn tại. Vui lòng kiểm tra lại.")
                return redirect("cart:cart_detail")

            if coupon.is_public_claim_template:
                messages.error(request, "Vui lòng nhận voucher trong trang tài khoản trước khi áp dụng mã này.")
                return redirect("cart:cart_detail")

            if coupon.assigned_user_id and coupon.assigned_user_id != request.user.id:
                messages.error(request, "Mã giảm giá này chỉ áp dụng cho tài khoản được tặng.")
                return redirect("cart:cart_detail")

            cart = Cart(request)
            subtotal_after_promotion = cart.get_coupon_eligible_subtotal_after_promotion()
            has_excluded_items = cart.has_coupon_excluded_items()

            if not coupon.is_valid():
                messages.error(request, "Mã giảm giá đã hết hạn hoặc chưa được kích hoạt.")
                return redirect("cart:cart_detail")

            if subtotal_after_promotion <= 0:
                messages.error(
                    request,
                    "Mã giảm giá không áp dụng cho sản phẩm đang trong Hot Deal hoặc Flash Sale."
                )
                return redirect("cart:cart_detail")

            if coupon.meets_min_order_amount(subtotal_after_promotion):
                previous_coupon_id = request.session.get("coupon_id")
                request.session["coupon_id"] = coupon.id
                if previous_coupon_id and previous_coupon_id != coupon.id:
                    messages.warning(request, "Mỗi đơn hàng chỉ áp dụng 1 mã giảm giá. Mã mới đã thay thế mã cũ.")
                if has_excluded_items:
                    messages.warning(
                        request,
                        "Sản phẩm đang trong Hot Deal hoặc Flash Sale sẽ không được giảm thêm bằng mã này."
                    )
                messages.success(request, f"Áp dụng mã {coupon.code} thành công.")
            else:
                messages.error(
                    request,
                    f"Mã {coupon.code} chỉ áp dụng cho đơn hàng từ {_format_vnd(coupon.min_order_amount)} đ."
                )
        else:
            messages.error(request, "Vui lòng nhập mã giảm giá hợp lệ.")

    return redirect("cart:cart_detail")


def remove(request):
    request.session.pop("coupon_id", None)
    messages.success(request, "Đã xóa mã giảm giá.")
    return redirect("cart:cart_detail")



