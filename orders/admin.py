from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Product, Order, OrderItem


def _send_order_status_email(order):
    recipient = order.customer_email or order.email
    if not recipient:
        return

    subject = f'[ShopTech] Cập nhật đơn hàng #{order.id}'
    if order.status == Order.STATUS_COMPLETED:
        message = f'Đơn hàng #{order.id} của bạn đã được admin duyệt và hoàn thành.'
        html_message = render_to_string('orders/email_status_update.html', {
            'order': order,
            'status': 'Đã duyệt và hoàn thành',
            'message': 'Đơn hàng của bạn đã được admin duyệt và hoàn thành. Cảm ơn bạn đã mua sắm!',
        })
    elif order.status == Order.STATUS_CANCELLED:
        message = f'Đơn hàng #{order.id} của bạn đã bị admin hủy.'
        html_message = render_to_string('orders/email_status_update.html', {
            'order': order,
            'status': 'Đã hủy',
            'message': 'Đơn hàng của bạn đã bị admin hủy. Nếu cần trợ giúp, vui lòng liên hệ bộ phận hỗ trợ.',
        })
    else:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
        html_message=html_message,
        fail_silently=True,
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'customer_email',
        'total_amount',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'customer_name',
        'customer_email',
    )

    actions = ['mark_as_completed', 'mark_as_cancelled']

    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous = self.model.objects.filter(pk=obj.pk).first()
            if previous:
                previous_status = previous.status

        super().save_model(request, obj, form, change)

        if change and previous_status != obj.status:
            _send_order_status_email(obj)

    def mark_as_completed(self, request, queryset):
        for order in queryset:
            order.status = Order.STATUS_COMPLETED
            order.save()
            _send_order_status_email(order)
        self.message_user(request, 'Đã cập nhật trạng thái thành completed và gửi email thông báo.')
    mark_as_completed.short_description = 'Đánh dấu là completed và gửi email'

    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            order.status = Order.STATUS_CANCELLED
            order.save()
            _send_order_status_email(order)
        self.message_user(request, 'Đã cập nhật trạng thái thành cancelled và gửi email thông báo.')
    mark_as_cancelled.short_description = 'Đánh dấu là cancelled và gửi email'





@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )