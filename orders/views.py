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
from urllib.parse import quote_plus
from datetime import datetime

from cart.cart import Cart
from core.notifications import create_order_created_notification

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .payment.sepay import Sepay

COD_FEE = 30000


def _format_vnd(value):
    return f'{int(round(value)):,}'.replace(',', '.') + ' đ'


def _send_confirmation_email(order):
    try:
        subject = f'[ShopTech] Xác nhận đơn hàng #{order.id}'
        order_total = _format_vnd(order.get_total_cost())
        html_message = render_to_string('orders/email_invoice.html', {
            'order': order,
            'order_items': order.items.all(),
        })
        send_mail(
            subject=subject,
            message=f'Đơn hàng #{order.id} của bạn đã được xác nhận. Tổng tiền: {order_total}',
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
            'phone': profile.phone,
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
                        'selected_discount': cart.get_discount(selected_product_ids),
                        'selected_total_price_after_discount': cart.get_total_price_after_discount(selected_product_ids),
                        'cod_fee': COD_FEE,
                    })

            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.city = order.province
                    order.customer_name = f'{order.first_name} {order.last_name}'.strip() or request.user.get_full_name() or request.user.username
                    order.customer_email = order.email or request.user.email
                    order.payment_method = payment_method
                    order.shipping_fee = COD_FEE if payment_method == Order.PAYMENT_COD else 0
                    order.total_amount = cart.get_total_price_after_discount(selected_product_ids) + order.shipping_fee
                    if payment_method == Order.PAYMENT_COD:
                        order.status = Order.STATUS_CONFIRMED
                    order.save()
                    create_order_created_notification(order)

                    profile = getattr(request.user, 'customer_profile', None)
                    if hasattr(profile, 'address'):
                        profile.phone = order.phone
                        profile.address = order.address
                        profile.ward = order.ward
                        profile.district = order.district
                        profile.province = order.province
                        profile.city = order.province
                        profile.postal_code = order.postal_code
                        profile.save()


                    for item in selected_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity'],
                        )
                        cart.remove(item['product'])
                    
                    coupon = cart.get_coupon()
                    if coupon:
                        coupon.delete()

                    cart.clear()
                    request.session.pop('coupon_id', None)

                try:
                    _send_confirmation_email(order)
                except Exception as e:
                    print(f'[EMAIL ERROR] Failed to send confirmation email: {e}')
                    
                if payment_method == 'sepay':
                    return redirect('orders:order_payment', order_id=order.id)

                messages.success(request, 'Đơn COD của bạn đã được ghi nhận. Shop sẽ xác nhận và chuẩn bị giao hàng.')
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
        'selected_discount': cart.get_discount(selected_product_ids),
        'selected_total_price_after_discount': cart.get_total_price_after_discount(selected_product_ids),
        'cod_fee': COD_FEE,
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
    qr_code_url = sepay.get_qr_code_url(order.id, order.total_amount)
    payment_url = qr_code_url  # Sepay QR tĩnh nên link & ảnh là một
    transfer_content = f"DH{order.id}"

    return render(request, 'orders/payment.html', {
        'order': order,
        'payment_url': payment_url,
        'qr_code_url': qr_code_url,
        'gateway_name': gateway_name,
        'transfer_content': transfer_content,
    })


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == Order.STATUS_PENDING:
        order.status = Order.STATUS_CANCELLED
        order.save()
        messages.warning(request, f'Đơn hàng #{order.id} đã được huỷ.')
    return redirect('orders:order_detail', order_id=order.id)


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
        order.paid = True
        order.status = Order.STATUS_CONFIRMED
        order.save()
        return render(request, 'orders/payment_return.html', {'success': True, 'order': order})

    order.status = Order.STATUS_CANCELLED
    order.save()
    return render(request, 'orders/payment_return.html', {'success': False, 'order': order, 'error': 'Thanh toán không thành công.'})


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user, status=Order.STATUS_COMPLETED)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
def order_tracking(request):
    active_statuses = [
        Order.STATUS_PENDING,
        Order.STATUS_CONFIRMED,
        Order.STATUS_PREPARING,
        Order.STATUS_SHIPPING,
        Order.STATUS_PROCESSING,
    ]
    orders = (
        Order.objects.filter(user=request.user, status__in=active_statuses)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'orders/tracking.html', {'orders': orders})


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

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def sepay_webhook(request):
    """
    Webhook handler for SePay.
    SePay sends a POST request with JSON data when a transaction matches the condition.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    # Lấy API Key từ header để xác thực
    # Cấu hình "Kiểu chứng thực": API Key
    auth_header = request.headers.get('Authorization', '')
    expected_api_key = getattr(settings, 'SEPAY_API_KEY', '')
    
    if not expected_api_key or f"Apikey {expected_api_key}" != auth_header:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        
        transfer_type = data.get('transferType') or data.get('gateway')  # some gateways use different field
        transfer_amount = data.get('transferAmount') or data.get('amount') or 0
        code = data.get('code')
        content = data.get('content', '') or ''

        # Nếu code trống, thử trích xuất mã đơn hàng từ nội dung giao dịch (vd: DH15)
        if not code:
            import re
            match = re.search(r'DH(\d+)', content, re.IGNORECASE)
            if match:
                code = f"DH{match.group(1)}"
        
        # Chấp nhận cả transferType='in' hoặc khi không có transferType (một số gateway)
        is_incoming = (not data.get('transferType')) or data.get('transferType') == 'in'
        
        if is_incoming and code and code.upper().startswith('DH'):
            try:
                order_id = int(code.upper().replace('DH', ''))
                order = Order.objects.get(id=order_id)
                
                # Cập nhật trạng thái thành công
                if int(float(transfer_amount)) >= int(order.total_amount):
                    order.paid = True
                    order.status = Order.STATUS_CONFIRMED  # Đã TT – Chờ shop xác nhận
                    order.save()
                    return JsonResponse({'success': True, 'message': 'Payment confirmed'})
                else:
                    return JsonResponse({'success': False, 'message': 'Insufficient amount'}, status=400)
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'message': 'Invalid order ID'}, status=400)
        
        # Không tìm thấy mã đơn, vẫn trả 200 để Sepay không retry
        return JsonResponse({'success': True, 'message': 'No matching order'})
                
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'success': True})
