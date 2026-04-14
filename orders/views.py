from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Order, OrderItem
from decimal import Decimal
from .payment.vnpay import VNPay

def checkout(request):
    # Lấy giỏ hàng từ session
    cart = request.session.get("cart", {})  # cart = {product_id: quantity}
    if not cart:
        return render(request, "checkout.html", {"error": "Giỏ hàng trống!"})

    # Tạo đơn hàng mới
    order = Order.objects.create(user=request.user)

    total = Decimal("0.00")
    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        if product.stock < qty:
            return render(request, "checkout.html", {"error": f"Sản phẩm {product.name} không đủ hàng!"})
        
        # Trừ kho
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

    # Logic phí vận chuyển
    address = request.POST.get("address", "")
    if "Hà Nội" in address and "nội thành" in address.lower():
        shipping_fee = Decimal("30000")
    else:
        shipping_fee = Decimal("50000")

    order.total_amount = total + shipping_fee
    order.shipping_fee = shipping_fee
    order.save()

    # Gửi email xác nhận
    send_mail(
        subject="Xác nhận đơn hàng",
        message=f"Đơn hàng #{order.id} đã được tạo. Tổng tiền: {order.total_amount} VND",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
    )

    # Xóa giỏ hàng
    request.session["cart"] = {}

    return render(request, "checkout_success.html", {"order": order})
