from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from core.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from coupon.forms import CouponApplyForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    coupon_form = CouponApplyForm()
    coupon = cart.get_coupon()
    selected_product_ids = set(cart.get_selected_product_ids())
    selected_items = []

    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
        if str(item['product'].id) in selected_product_ids:
            selected_items.append(item)

    return render(request, 'cart/detail.html', {
        'cart': cart,
        'coupon_form': coupon_form,
        'coupon': coupon,
        'selected_product_ids': selected_product_ids,
        'selected_items': selected_items,
        'selected_count': sum(item['quantity'] for item in selected_items),
        'selected_total_price': cart.get_total_price(selected_product_ids),
        'selected_discount': cart.get_discount(selected_product_ids),
        'selected_total_price_after_discount': cart.get_total_price_after_discount(selected_product_ids),
    })


@require_POST
def cart_checkout(request):
    cart = Cart(request)
    selected_product_ids = request.POST.getlist('selected_products')
    if not selected_product_ids:
        messages.warning(request, 'Vui lòng chọn ít nhất một sản phẩm để thanh toán.')
        return redirect('cart:cart_detail')

    cart.set_selected_product_ids(selected_product_ids)
    return redirect('orders:order_create')
