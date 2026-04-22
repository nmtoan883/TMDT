from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages

from .models import Product, Order, OrderItem
from .services import deduct_stock_for_completed_order


def _send_order_status_email(order):
    recipient = order.customer_email or order.email
    if not recipient:
        return

    subject = f'[ShopTech] Cập nhật đơn hàng #{order.id}'
    status_labels = {
        Order.STATUS_CONFIRMED: ('Chờ xác nhận', 'Đơn hàng của bạn đã được xác nhận và đang chờ đóng gói.'),
        Order.STATUS_PREPARING: ('Đang chuẩn bị', 'Đơn hàng của bạn đang được đóng gói, sắp sẵn sàng giao đi.'),
        Order.STATUS_SHIPPING:  ('Đang giao hàng', 'Đơn hàng của bạn đang trên đường giao đến bạn.'),
        Order.STATUS_COMPLETED: ('Đã giao hàng', 'Đơn hàng của bạn đã được giao thành công. Cảm ơn đã mua sắm!'),
        Order.STATUS_CANCELLED: ('Đã huỷ', 'Đơn hàng của bạn đã bị huỷ. Vui lòng liên hệ hỗ trợ nếu cần.'),
    }
    if order.status not in status_labels:
        return

    status_text, body = status_labels[order.status]
    try:
        html_message = render_to_string('orders/email_status_update.html', {
            'order': order,
            'status': status_text,
            'message': body,
        })
    except Exception:
        html_message = None

    send_mail(
        subject=subject,
        message=f'Đơn hàng #{order.id}: {body}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
        html_message=html_message,
        fail_silently=True,
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer_name',
        'customer_email',
        'total_amount',
        'status_badge',
        'paid_badge',
        'payment_method',
        'created_at',
    )

    list_filter = ('status', 'paid', 'payment_method', 'created_at')

    search_fields = ('customer_name', 'customer_email', 'id')

    readonly_fields = ('created_at', 'paid', 'action_buttons')

    fieldsets = (
        ('Thao tác nhanh', {
            'fields': ('action_buttons',),
        }),
        ('Thông tin đơn hàng', {
            'fields': ('status', 'paid', 'payment_method', 'total_amount', 'created_at'),
        }),
        ('Thông tin khách hàng', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'ward', 'district', 'province', 'postal_code'),
        }),
    )

    actions = ['mark_as_confirmed', 'mark_as_preparing', 'mark_as_shipping', 'mark_as_completed', 'mark_as_cancelled']

    inlines = [OrderItemInline]

    # ── Custom URLs ──────────────────────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:order_id>/confirm/', self.admin_site.admin_view(self.confirm_order), name='orders_order_confirm'),
            path('<int:order_id>/reject/', self.admin_site.admin_view(self.reject_order),  name='orders_order_reject'),
            path('<int:order_id>/set-status/<str:new_status>/', self.admin_site.admin_view(self.set_status), name='orders_order_set_status'),
        ]
        return custom + urls

    def confirm_order(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order.status = Order.STATUS_PREPARING
        order.save()
        _send_order_status_email(order)
        messages.success(request, f'✅ Đơn hàng #{order_id} đã được XÁC NHẬN → Chờ lấy hàng.')
        return HttpResponseRedirect(reverse('admin:orders_order_change', args=[order_id]))

    def reject_order(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order.status = Order.STATUS_CANCELLED
        order.save()
        _send_order_status_email(order)
        messages.warning(request, f'❌ Đơn hàng #{order_id} đã bị TỪ CHỐI và huỷ.')
        return HttpResponseRedirect(reverse('admin:orders_order_change', args=[order_id]))

    def set_status(self, request, order_id, new_status):
        allowed = [s for s, _ in Order.STATUS_CHOICES]
        if new_status in allowed:
            order = Order.objects.get(pk=order_id)
            if new_status == Order.STATUS_COMPLETED:
                try:
                    deduct_stock_for_completed_order(order)
                except Exception as exc:
                    messages.error(request, str(exc))
                    return HttpResponseRedirect(reverse('admin:orders_order_change', args=[order_id]))
            order.status = new_status
            if new_status == Order.STATUS_COMPLETED and order.payment_method == Order.PAYMENT_COD:
                order.paid = True
            order.save()
            _send_order_status_email(order)
            messages.success(request, f'Đơn hàng #{order_id} → {order.get_status_display()}')
        return HttpResponseRedirect(reverse('admin:orders_order_change', args=[order_id]))

    # ── Readonly field: action buttons ───────────────────────────────────────

    def action_buttons(self, obj):
        if not obj.pk:
            return '—'

        stage_map = {
            'pending': [
                ('Xác nhận đơn (Chờ xác nhận)', reverse('admin:orders_order_confirm', args=[obj.pk]), '#9b59b6'),
                ('Từ chối / Huỷ', reverse('admin:orders_order_reject', args=[obj.pk]), '#d9534f'),
            ],
            'confirmed': [
                ('✅ Xác nhận → Chuẩn bị hàng', reverse('admin:orders_order_confirm', args=[obj.pk]), '#e67e22'),
                ('❌ Từ chối / Huỷ', reverse('admin:orders_order_reject', args=[obj.pk]), '#d9534f'),
            ],
            'preparing': [
                ('🚚 Chuyển → Đang giao hàng', reverse('admin:orders_order_set_status', args=[obj.pk, 'shipping']), '#3498db'),
                ('❌ Huỷ đơn', reverse('admin:orders_order_reject', args=[obj.pk]), '#d9534f'),
            ],
            'shipping': [
                ('✅ Xác nhận đã giao thành công', reverse('admin:orders_order_set_status', args=[obj.pk, 'completed']), '#5cb85c'),
                ('❌ Huỷ đơn', reverse('admin:orders_order_reject', args=[obj.pk]), '#d9534f'),
            ],
            'completed': [],
            'cancelled': [],
        }

        btns = stage_map.get(obj.status, [])
        if not btns:
            label_map = {'completed': '✅ Đơn đã hoàn thành', 'cancelled': '❌ Đơn đã huỷ'}
            return format_html(
                '<span style="color:#888;">{}</span>',
                label_map.get(obj.status, 'Không có thao tác khả dụng')
            )

        html_parts = []
        for label, url, color in btns:
            html_parts.append(
                f'<a href="{url}" style="display:inline-block;margin:4px 8px 4px 0;padding:8px 18px;'
                f'background:{color};color:white;border-radius:4px;font-weight:bold;'
                f'font-size:13px;text-decoration:none;">{label}</a>'
            )
        return format_html('<div style="margin:5px 0;">{}</div>', ''.join(html_parts))

    action_buttons.short_description = 'Xác nhận / Từ chối'
    action_buttons.allow_tags = True

    # ── Badge helpers ─────────────────────────────────────────────────────────

    def status_badge(self, obj):
        colors = {
            'pending':    ('#f0ad4e', '⏰ Chờ thanh toán'),
            'confirmed':  ('#9b59b6', '🔔 Chờ xác nhận'),
            'preparing':  ('#e67e22', '📦 Chờ lấy hàng'),
            'shipping':   ('#3498db', '🚚 Đang giao hàng'),
            'completed':  ('#5cb85c', '✅ Đã giao hàng'),
            'cancelled':  ('#d9534f', '❌ Đã huỷ'),
            'processing': ('#5bc0de', '🔄 Đang xử lý'),
        }
        color, label = colors.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;font-size:12px;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Trạng thái'

    def paid_badge(self, obj):
        if obj.paid:
            return format_html('<span style="background:#5cb85c;color:white;padding:3px 8px;border-radius:4px;font-size:12px;">✓ Đã TT</span>')
        return format_html('<span style="background:#d9534f;color:white;padding:3px 8px;border-radius:4px;font-size:12px;">✗ Chưa TT</span>')
    paid_badge.short_description = 'Thanh toán'

    # ── save_model ─────────────────────────────────────────────────────────────

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous = self.model.objects.filter(pk=obj.pk).first()
            if previous:
                previous_status = previous.status
        super().save_model(request, obj, form, change)
        if change and previous_status != obj.status:
            _send_order_status_email(obj)

    # ── Bulk actions ───────────────────────────────────────────────────────────

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status=Order.STATUS_CONFIRMED)
        self.message_user(request, f'{queryset.count()} đơn → Chờ xác nhận.')
    mark_as_confirmed.short_description = '🔔 Chờ xác nhận'

    def mark_as_preparing(self, request, queryset):
        queryset.update(status=Order.STATUS_PREPARING)
        self.message_user(request, f'{queryset.count()} đơn → Chờ lấy hàng.')
    mark_as_preparing.short_description = '📦 Chờ lấy hàng'

    def mark_as_shipping(self, request, queryset):
        queryset.update(status=Order.STATUS_SHIPPING)
        self.message_user(request, f'{queryset.count()} đơn → Đang giao hàng.')
    mark_as_shipping.short_description = '🚚 Đang giao hàng'

    def mark_as_completed(self, request, queryset):
        for order in queryset:
            try:
                deduct_stock_for_completed_order(order)
            except Exception as exc:
                self.message_user(request, f'Không thể hoàn tất đơn #{order.id}: {exc}', level=messages.ERROR)
                continue
            order.status = Order.STATUS_COMPLETED
            if order.payment_method == Order.PAYMENT_COD:
                order.paid = True
            order.save()
            _send_order_status_email(order)
        self.message_user(request, f'{queryset.count()} đơn đã hoàn thành & gửi email.')
    mark_as_completed.short_description = '✅ Đã giao hàng & gửi email'

    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            order.status = Order.STATUS_CANCELLED
            order.save()
            _send_order_status_email(order)
        self.message_user(request, f'{queryset.count()} đơn đã huỷ & gửi email.')
    mark_as_cancelled.short_description = '❌ Huỷ đơn & gửi email'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')



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
        'status_badge',
        'paid_badge',
        'payment_method',
        'created_at',
    )

    list_filter = (
        'status',
        'paid',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'customer_name',
        'customer_email',
        'id',
    )

    readonly_fields = ('created_at', 'paid')

    actions = ['mark_as_confirmed', 'mark_as_preparing', 'mark_as_shipping', 'mark_as_completed', 'mark_as_cancelled']

    inlines = [OrderItemInline]

    def status_badge(self, obj):
        colors = {
            'pending':    ('#f0ad4e', '⏰ Chờ thanh toán'),
            'confirmed':  ('#9b59b6', '✅ Chờ xác nhận'),
            'preparing':  ('#e67e22', '📦 Chờ lấy hàng'),
            'shipping':   ('#3498db', '🚚 Đang giao hàng'),
            'completed':  ('#5cb85c', '✅ Đã giao hàng'),
            'cancelled':  ('#d9534f', '❌ Đã huỷ'),
            'processing': ('#5bc0de', '🔄 Đang xử lý'),
        }
        color, label = colors.get(obj.status, ('#999', obj.status))
        return f'<span style="background:{color};color:white;padding:3px 8px;border-radius:4px;font-size:12px;">{label}</span>'
    status_badge.short_description = 'Trạng thái'
    status_badge.allow_tags = True

    def paid_badge(self, obj):
        if obj.paid:
            return '<span style="background:#5cb85c;color:white;padding:3px 8px;border-radius:4px;font-size:12px;">✓ Đã TT</span>'
        return '<span style="background:#d9534f;color:white;padding:3px 8px;border-radius:4px;font-size:12px;">✗ Chưa TT</span>'
    paid_badge.short_description = 'Thanh toán'
    paid_badge.allow_tags = True

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous = self.model.objects.filter(pk=obj.pk).first()
            if previous:
                previous_status = previous.status

        super().save_model(request, obj, form, change)

        if change and previous_status != obj.status:
            _send_order_status_email(obj)

    def mark_as_processing(self, request, queryset):
        queryset.update(status=Order.STATUS_PROCESSING)
        self.message_user(request, f'{queryset.count()} đơn → Đang xử lý.')
    mark_as_processing.short_description = '🔄 Đang xử lý'

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status=Order.STATUS_CONFIRMED)
        self.message_user(request, f'{queryset.count()} đơn → Chờ xác nhận.')
    mark_as_confirmed.short_description = '✅ Chờ xác nhận'

    def mark_as_preparing(self, request, queryset):
        queryset.update(status=Order.STATUS_PREPARING)
        self.message_user(request, f'{queryset.count()} đơn → Chờ lấy hàng.')
    mark_as_preparing.short_description = '📦 Chờ lấy hàng'

    def mark_as_shipping(self, request, queryset):
        queryset.update(status=Order.STATUS_SHIPPING)
        self.message_user(request, f'{queryset.count()} đơn → Đang giao hàng.')
    mark_as_shipping.short_description = '🚚 Đang giao hàng'

    def mark_as_completed(self, request, queryset):
        for order in queryset:
            try:
                deduct_stock_for_completed_order(order)
            except Exception as exc:
                self.message_user(request, f'Không thể hoàn tất đơn #{order.id}: {exc}', level=messages.ERROR)
                continue
            order.status = Order.STATUS_COMPLETED
            if order.payment_method == Order.PAYMENT_COD:
                order.paid = True
            order.save()
            _send_order_status_email(order)
        self.message_user(request, f'{queryset.count()} đơn hàng đã hoàn thành và gửi email thông báo.')
    mark_as_completed.short_description = '✅ Đánh dấu Đã giao hàng & gửi email'

    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            order.status = Order.STATUS_CANCELLED
            order.save()
            _send_order_status_email(order)
        self.message_user(request, f'{queryset.count()} đơn hàng đã bị huỷ và gửi email thông báo.')
    mark_as_cancelled.short_description = '❌ Huỷ đơn hàng & gửi email'





@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )
