from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from urllib.parse import quote_plus
from datetime import datetime

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem


@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Gio hang dang trong.')
        return redirect('cart:cart_detail')

    initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
    }

    profile = getattr(request.user, 'customer_profile', None)
    if profile is not None:
        initial.update(
            {
                'address': profile.address,
                'province': profile.province or profile.city,
                'district': profile.district,
                'ward': profile.ward,
                'postal_code': profile.postal_code,
            }
        )

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.city = order.province
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            request.session['coupon_id'] = None
            
            if order.payment_method == Order.PAYMENT_SEPAY:
                # Chuyển hướng đến thanh toán SePay
                return redirect('orders:sepay_payment', order_id=order.id)
            else:
                # COD - đánh dấu đã thanh toán khi nhận hàng
                messages.success(request, f'Da tao don hang #{order.id} thanh cong. Ban se thanh toan khi nhan hang.')
                return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderCreateForm(initial=initial)

    return render(request, 'orders/create.html', {'cart': cart, 'form': form})


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created')
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


@login_required
def sepay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_method != Order.PAYMENT_SEPAY:
        messages.warning(request, 'Don hang nay khong su dung SePay.')
        return redirect('orders:order_detail', order_id=order.id)

    if order.paid:
        messages.info(request, 'Don hang da duoc thanh toan.')
        return redirect('orders:order_detail', order_id=order.id)

    account_number = getattr(settings, 'SEPAY_ACCOUNT_NUMBER', '0123456789')
    account_name = getattr(settings, 'SEPAY_ACCOUNT_NAME', 'SePay Test Account')

    content = f"Thanh toan don hang {order.id}"
    amount = int(order.get_total_cost())
    encoded_content = quote_plus(content)

    if account_number.startswith('YOUR_') or account_name.startswith('YOUR_'):
        payment_text = f"Tai khoan: {account_number}\nTen: {account_name}\nSo tien: {amount} VND\nNoi dung: {content}"
        payment_url = f"https://api.qrserver.com/v1/create-qr-code/?size=320x320&data={quote_plus(payment_text)}"
    else:
        payment_url = (
            f"https://qr.sepay.vn/img?acc={account_number}"
            f"&bank=MB&amount={amount}&des={encoded_content}&template=compact"
        )

    context = {
        'order': order,
        'payment_url': payment_url,
        'sepay_qr_url': payment_url,
        'amount': amount,
        'content': content,
        'account_number': account_number,
        'account_name': account_name,
        'sepay_bank_name': 'MB',
    }

    return render(request, 'orders/sepay_payment.html', context)


@login_required
def sepay_callback(request):
    # Xử lý callback từ SePay (nếu có webhook)
    # Trong trường hợp đơn giản, có thể kiểm tra thủ công
    return redirect('orders:order_history')
