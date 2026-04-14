from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem


def _send_confirmation_email(order):
    try:
        subject = f'[ShopTech] Xác nhận đơn hàng #{order.id}'
        html_message = render_to_string('orders/email_invoice.html', {
            'order': order,
            'order_items': order.items.all(),
        })
        send_mail(
            subject=subject,
            message=f'Đơn hàng #{order.id} của bạn đã được xác nhận. Tổng tiền: {order.get_total_cost()}đ',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f'[EMAIL ERROR] Không gửi được email cho đơn #{order.id}: {e}')


@login_required
def order_create(request):
    cart = Cart(request)
    selected_product_ids = cart.get_selected_product_ids()
    selected_items = cart.get_selected_items()

    if len(cart) == 0:
        messages.warning(request, 'Giỏ hàng đang trống.')
        return redirect('cart:cart_detail')

    if not selected_items:
        messages.warning(request, 'Vui lòng chọn ít nhất một sản phẩm để thanh toán.')
        return redirect('cart:cart_detail')

    initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
    }

    profile = getattr(request.user, 'customer_profile', None)
    if profile is not None:
        initial.update({
            'address': profile.address,
            'province': profile.province or profile.city,
            'district': profile.district,
            'ward': profile.ward,
            'postal_code': profile.postal_code,
        })

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            for item in selected_items:
                if item['product'].stock < item['quantity']:
                    messages.error(
                        request,
                        f'Sản phẩm "{item["product"].name}" chỉ còn {item["product"].stock} cái trong kho, không đủ số lượng!'
                    )
                    return render(request, 'checkout.html', {
                        'cart': cart,
                        'form': form,
                        'selected_items': selected_items,
                        'selected_total_price': cart.get_total_price(selected_product_ids),
                        'selected_total_price_after_discount': cart.get_total_price_after_discount(selected_product_ids),
                    })

            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.city = order.province
                    order.save()

                    for item in selected_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity'],
                        )
                        item['product'].stock -= item['quantity']
                        item['product'].save()
                        cart.remove(item['product'])

                _send_confirmation_email(order)
                messages.success(request, f'Đã tạo đơn hàng #{order.id} thành công.')
                return redirect('orders:order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, 'Có lỗi xảy ra khi tạo đơn hàng. Vui lòng thử lại!')
                print(f'[ORDER ERROR] {e}')
    else:
        form = OrderCreateForm(initial=initial)

    return render(request, 'checkout.html', {
        'cart': cart,
        'form': form,
        'selected_items': selected_items,
        'selected_total_price': cart.get_total_price(selected_product_ids),
        'selected_total_price_after_discount': cart.get_total_price_after_discount(selected_product_ids),
    })


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created')
    )
    return render(request, 'orders/history_v2.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user,
    )
    return render(request, 'orders/detail_v2.html', {'order': order})


@api_view(['POST'])
def checkout(request):
    # Lấy giỏ hàng từ session
    cart = request.session.get("cart", {})  # cart = {product_id: quantity}
    if not cart:
        return render(request, "checkout.html", {"error": "Giỏ hàng trống!"})

    # Tạo đơn hàng mới
    order = Order.objects.create(user=request.user)

    if location == 'noi_thanh':
        shipping_fee = 30000
    elif location == 'ngoai_thanh':
        shipping_fee = 50000
    else:
        shipping_fee = Decimal("50000")

    order.total_amount = total + shipping_fee
    order.shipping_fee = shipping_fee
    order.save()

    if payment_method == 'momo':
        payment_status = 'Thanh toán qua MoMo'
    elif payment_method == 'zalopay':
        payment_status = 'Thanh toán qua ZaloPay'
    elif payment_method == 'cod':
        payment_status = 'Thanh toán khi nhận hàng'
    else:
        return Response({'error': 'Phương thức không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'amount': amount,
        'shipping_fee': shipping_fee,
        'total': total,
        'payment_method': payment_method,
        'payment_status': payment_status,
    })
