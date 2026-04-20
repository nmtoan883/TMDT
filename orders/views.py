from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .payment.sepay import Sepay


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
            payment_method = form.cleaned_data.get('payment_method', 'sepay')
            for item in selected_items:
                if item['product'].stock < item['quantity']:
                    messages.error(
                        request,
                        f'Sản phẩm "{item["product"].name}" chỉ còn {item["product"].stock} cái trong kho, không đủ số lượng!'
                    )
                    return render(request, 'orders/create.html', {
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
                    order.customer_name = f'{order.first_name} {order.last_name}'.strip() or request.user.get_full_name() or request.user.username
                    order.customer_email = order.email or request.user.email
                    order.payment_method = payment_method
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
                if payment_method == 'sepay':
                    sepay = Sepay()
                    return_url = request.build_absolute_uri(reverse('orders:payment_return'))
                    payment_url = sepay.create_payment_url(order.id, order.total_amount, return_url)
                    qr_code_url = sepay.get_qr_code_url(payment_url)
                    return render(request, 'orders/payment.html', {
                        'order': order,
                        'payment_url': payment_url,
                        'qr_code_url': qr_code_url,
                        'gateway_name': 'Sepay',
                    })

                messages.success(
                    request,
                    'Đơn hàng của bạn đã được gửi yêu cầu duyệt. Admin sẽ kiểm tra và cập nhật trạng thái trong thời gian sớm nhất.'
                )
                return redirect('orders:order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, 'Có lỗi xảy ra khi tạo đơn hàng. Vui lòng thử lại!')
                print(f'[ORDER ERROR] {e}')
    else:
        form = OrderCreateForm(initial=initial)

    return render(request, 'orders/create.html', {
        'cart': cart,
        'form': form,
        'selected_items': selected_items,
        'selected_total_price': cart.get_total_price(selected_product_ids),
        'selected_total_price_after_discount': cart.get_total_price_after_discount(selected_product_ids),
    })


@login_required
def order_payment(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user,
    )

    if order.status == Order.STATUS_COMPLETED:
        return redirect('orders:order_detail', order_id=order.id)

    if order.payment_method != Order.PAYMENT_SEPAY:
        return redirect('orders:order_detail', order_id=order.id)

    payment_method = request.session.pop('payment_method', 'sepay')
    gateway_name = 'Sepay' if payment_method == 'sepay' else payment_method.title()

    sepay = Sepay()
    return_url = request.build_absolute_uri(reverse('orders:payment_return'))
    payment_url = sepay.create_payment_url(order.id, order.total_amount, return_url)
    qr_code_url = sepay.get_qr_code_url(payment_url)

    return render(request, 'orders/payment.html', {
        'order': order,
        'payment_url': payment_url,
        'qr_code_url': qr_code_url,
        'gateway_name': gateway_name,
    })


@login_required
def payment_return(request):
    order_id = request.GET.get('order_id') or request.GET.get('vnp_TxnRef')
    response_code = request.GET.get('status') or request.GET.get('vnp_ResponseCode') or request.GET.get('vnp_ResponseCode')

    if not order_id:
        return render(request, 'orders/payment_return.html', {'success': False, 'error': 'Không tìm thấy đơn hàng.'})

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return render(request, 'orders/payment_return.html', {'success': False, 'error': 'Không tìm thấy đơn hàng.'})

    if response_code and str(response_code).lower() in ['00', 'success', 'ok', 'paid', 'completed']:
        order.status = Order.STATUS_COMPLETED
        order.save()
        return render(request, 'orders/payment_return.html', {'success': True, 'order': order})

    order.status = Order.STATUS_CANCELLED
    order.save()
    return render(request, 'orders/payment_return.html', {'success': False, 'order': order, 'error': 'Thanh toán không thành công.'})


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user,
    )
    return render(request, 'orders/detail.html', {'order': order})


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
