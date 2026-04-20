from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render

from orders.models import Order, OrderItem, Product
from orders.payment.sepay import Sepay

from .forms import CouponApplyForm
from .models import Coupon


def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return render(request, "checkout.html", {"error": "Giỏ hàng trống!"})

    # Tạo đơn hàng
    order = Order.objects.create(user=request.user)

    total = Decimal("0.00")

    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)

        if product.stock < qty:
            return render(
                request,
                "checkout.html",
                {"error": f"Sản phẩm {product.name} không đủ hàng!"}
            )

        product.stock -= qty
        product.save()

        item_total = product.price * qty
        total += item_total

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=product.price
        )

    # Phí ship
    address = request.POST.get("address", "")

    if "Hà Nội" in address and "nội thành" in address.lower():
        shipping_fee = Decimal("30000")
    else:
        shipping_fee = Decimal("50000")

    order.total_amount = total + shipping_fee
    order.status = "pending"
    order.save()

    # Gửi email
    send_mail(
        subject="Xác nhận đơn hàng",
        message=f"Đơn hàng #{order.id} đã được tạo. Tổng tiền: {order.total_amount} VND",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
    )

    # Tạo link thanh toán Sepay
    sepay = Sepay()
    return_url = request.build_absolute_uri('/coupon/payment_return/')
    payment_url = sepay.create_payment_url(
        order_id=order.id,
        amount=int(order.total_amount),
        return_url=return_url,
    )

    # Xóa giỏ hàng
    request.session["cart"] = {}

    return redirect(payment_url)


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


def payment_return(request):
    response_code = request.GET.get("vnp_ResponseCode")
    order_id = request.GET.get("vnp_TxnRef")

    try:
        order = Order.objects.get(id=order_id)

        if response_code == "00":
            order.status = "paid"
            order.save()

            return render(
                request,
                "checkout_success.html",
                {"order": order}
            )
        else:
            order.status = "failed"
            order.save()

            return HttpResponse("Thanh toán thất bại")

    except Order.DoesNotExist:
        return HttpResponse("Không tìm thấy đơn hàng")
