from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderItem

# ==============================================================

# ==============================================================



@login_required
def checkout(request):
    """
    Trang checkout - xử lý toàn bộ luồng đặt hàng:
    1. Hiển thị form nhập thông tin giao hàng
    2. Kiểm tra giỏ hàng không rỗng
    3. Kiểm tra stock từng sản phẩm
    4. Tạo Order + trừ stock trong 1 transaction
    5. Gửi email xác nhận
    """


    # =====================================================

    if request.method == 'GET':
        # Tính tổng tiền để hiển thị
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'orders/checkout.html', {
            'cart_items': cart_items,
            'total': total,
        })

    # ---- Xử lý khi user nhấn "Đặt hàng" (POST) ----
    if request.method == 'POST':

        # Bước 1: Kiểm tra giỏ hàng không rỗng
        if not cart_items:
            messages.error(request, 'Giỏ hàng của bạn đang trống!')
            return redirect('cart')  # Đổi 'cart' thành tên URL giỏ hàng thật

        # Bước 2: Lấy dữ liệu từ form
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        note = request.POST.get('note', '').strip()

        # Bước 3: Validate form cơ bản
        if not full_name or not phone or not address:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin giao hàng!')
            total = sum(item.product.price * item.quantity for item in cart_items)
            return render(request, 'orders/checkout.html', {
                'cart_items': cart_items,
                'total': total,
            })

        # Bước 4: Kiểm tra stock từng sản phẩm TRƯỚC khi tạo đơn
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(
                    request,
                    f'Sản phẩm "{item.product.name}" chỉ còn {item.product.stock} cái, '
                    f'bạn đang chọn {item.quantity} cái!'
                )
                total = sum(i.product.price * i.quantity for i in cart_items)
                return render(request, 'orders/checkout.html', {
                    'cart_items': cart_items,
                    'total': total,
                })

        try:
            with transaction.atomic():
                total_price = sum(item.product.price * item.quantity for item in cart_items)

                # Tạo đơn hàng
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    note=note,
                    total_price=total_price,
                )

                # Tạo từng OrderItem + trừ stock
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,  # Lưu giá tại thời điểm mua
                    )
                    # Trừ stock (dùng select_for_update để tránh race condition)
                    item.product.stock -= item.quantity
                    item.product.save()

                # Xóa giỏ hàng sau khi đặt thành công
           

        except Exception as e:
            messages.error(request, 'Có lỗi xảy ra khi đặt hàng. Vui lòng thử lại!')
            # Log lỗi để debug (sau này có thể dùng logging thật)
            print(f'[ORDER ERROR] {e}')
            return redirect('checkout')

        # Bước 6: Gửi email xác nhận (ngoài transaction để không block)
        _send_confirmation_email(order)

        # Bước 7: Chuyển sang trang thành công
        messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: #{order.id}')
        return redirect('order_success', order_id=order.id)


@login_required
def order_success(request, order_id):
    """Trang xác nhận sau khi đặt hàng thành công."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history(request):
    """
    Trang lịch sử đơn hàng - dành cho thành viên 2 (Profile Expert) dùng.
    Bạn tạo sẵn view này để nhóm ghép dễ hơn.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Chi tiết 1 đơn hàng - dùng cho trang Theo dõi đơn hàng."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# =================================
# ==============================================================

def _send_confirmation_email(order):
    """
    Gửi email xác nhận đơn hàng kèm hóa đơn.
    Dùng fail_silently=True để lỗi email không crash cả web.
    """
    try:
        subject = f'[ShopTech] Xác nhận đơn hàng #{order.id}'

        # Render nội dung email từ template HTML
        html_message = render_to_string('orders/email_invoice.html', {
            'order': order,
            'order_items': order.items.all(),
        })

        send_mail(
            subject=subject,
            message=f'Đơn hàng #{order.id} của bạn đã được xác nhận. Tổng tiền: {order.total_price}đ',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=True,  # Quan trọng: lỗi email không crash app
        )
    except Exception as e:
        print(f'[EMAIL ERROR] Không gửi được email cho đơn #{order.id}: {e}')
