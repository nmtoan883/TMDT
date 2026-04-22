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
        current_quantity = cart.cart.get(str(product.id), {}).get('quantity', 0)
        requested_quantity = cd['quantity'] if cd['override'] else current_quantity + cd['quantity']

        if product.stock <= 0:
            messages.error(request, f'Sản phẩm "{product.name}" hiện đã hết hàng.')
            return redirect('cart:cart_detail')

        if requested_quantity > product.stock:
            messages.warning(
                request,
                f'Sản phẩm "{product.name}" chỉ còn {product.stock} sản phẩm trong kho.'
            )
            if current_quantity > product.stock or cd['override']:
                cart.add(product=product, quantity=product.stock, override_quantity=True)
            return redirect('cart:cart_detail')

        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
        messages.success(request, f'Đã cập nhật "{product.name}" trong giỏ hàng.')
    else:
        messages.error(request, 'Số lượng sản phẩm không hợp lệ.')
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
    cart_items = list(cart)
    selected_items = []

    for item in cart_items:
        item['line_total_value'] = int(item['total_price'])
        item['promotion_discount_value'] = int(item.get('promotion_discount', 0))
        item['coupon_eligible_total_value'] = 0 if item.get('coupon_excluded') else int(item['total_price_after_promotion'])
        if str(item['product'].id) in selected_product_ids:
            selected_items.append(item)

    return render(request, 'cart/detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'coupon_form': coupon_form,
        'coupon': coupon,
        'coupon_discount_percent': coupon.discount_percent if coupon else 0,
        'coupon_discount_amount': int(coupon.discount_amount or 0) if coupon else 0,
        'coupon_min_order_amount': int(coupon.min_order_amount or 0) if coupon else 0,
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

    for item in cart.get_items(selected_product_ids):
        if item['quantity'] > item['product'].stock:
            messages.error(
                request,
                f'Sản phẩm "{item["product"].name}" chỉ còn {item["product"].stock} sản phẩm trong kho.'
            )
            return redirect('cart:cart_detail')

    cart.set_selected_product_ids(selected_product_ids)
    return redirect('orders:order_create')
