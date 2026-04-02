from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Hiển thị danh sách sản phẩm ngay trong trang chi tiết đơn hàng."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_subtotal')

    def get_subtotal(self, obj):
        return f"{obj.get_subtotal():,}đ"
    get_subtotal.short_description = 'Thành tiền'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    list_editable = ('status',)  # Đổi trạng thái ngay trên danh sách
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items')
