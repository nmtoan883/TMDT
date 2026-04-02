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
