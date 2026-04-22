from django.urls import reverse

from .models import UserNotification


def create_reward_coupon_notification(order, coupon):
    if not order.user_id or not coupon:
        return None

    min_amount = f'{coupon.min_order_amount:,.0f}'.replace(',', '.') + ' đ'
    return UserNotification.objects.create(
        user=order.user,
        order=order,
        notification_type=UserNotification.TYPE_ORDER,
        title='Bạn vừa nhận được voucher mới',
        message=f'Mã {coupon.code} giảm {coupon.discount_percent}% cho đơn từ {min_amount} đã được thêm vào kho voucher.',
        action_url=reverse('accounts:dashboard') + '#voucher-wallet',
    )


def create_order_created_notification(order):
    if not order.user_id:
        return None

    return UserNotification.objects.create(
        user=order.user,
        order=order,
        notification_type=UserNotification.TYPE_ORDER,
        title=f'Đặt hàng thành công #{order.id}',
        message='Shop đã nhận đơn hàng của bạn. Bạn sẽ nhận thêm thông báo khi đơn được xác nhận.',
        action_url=reverse('orders:order_detail', args=[order.id]),
    )


def create_order_status_notification(order, new_status):
    if not order.user_id:
        return None

    notification_data = {
        order.STATUS_CONFIRMED: {
            'notification_type': UserNotification.TYPE_ORDER,
            'title': f'Đơn hàng #{order.id} đã được xác nhận',
            'message': 'Shop đã xác nhận đơn hàng của bạn và sẽ sớm chuẩn bị giao hàng.',
            'action_url': reverse('orders:order_detail', args=[order.id]),
        },
        order.STATUS_PREPARING: {
            'notification_type': UserNotification.TYPE_ORDER,
            'title': f'Đơn hàng #{order.id} đang được chuẩn bị',
            'message': 'Shop đã xác nhận và đang chuẩn bị hàng để giao cho bạn.',
            'action_url': reverse('orders:order_detail', args=[order.id]),
        },
        order.STATUS_COMPLETED: {
            'notification_type': UserNotification.TYPE_REVIEW,
            'title': f'Đơn hàng #{order.id} đã giao thành công',
            'message': 'Cảm ơn bạn đã mua hàng. Hãy dành một chút thời gian đánh giá sản phẩm nhé.',
            'action_url': reverse('orders:order_detail', args=[order.id]) + '#review-products',
        },
    }

    data = notification_data.get(new_status)
    if not data:
        return None

    notification = UserNotification.objects.create(
        user=order.user,
        order=order,
        notification_type=data['notification_type'],
        title=data['title'],
        message=data['message'],
        action_url=data['action_url'],
    )
    return notification
