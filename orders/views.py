
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
            messages.success(request, f'Da tao don hang #{order.id} thanh cong.')
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderCreateForm(initial=initial)

    return render(request, 'checkout.html', {'cart': cart, 'form': form})


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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def checkout(request):
    data = request.data

    amount = float(data.get('amount', 0))
    location = data.get('location')
    payment_method = data.get('payment_method')

    # ===== phí ship =====
    if location == 'noi_thanh':
        shipping_fee = 30000
    elif location == 'ngoai_thanh':
        shipping_fee = 50000
    else:
        return Response({'error': 'Địa điểm không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

    total = amount + shipping_fee

    # ===== thanh toán =====
    if payment_method == 'momo':
        payment_status = "Thanh toán qua MoMo"
    elif payment_method == 'zalopay':
        payment_status = "Thanh toán qua ZaloPay"
    elif payment_method == 'cod':
        payment_status = "Thanh toán khi nhận hàng"
    else:
        return Response({'error': 'Phương thức không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "amount": amount,
        "shipping_fee": shipping_fee,
        "total": total,
        "payment_method": payment_method,
        "payment_status": payment_status
    })

