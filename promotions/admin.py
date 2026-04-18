from django.contrib import admin
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'discount_type',
        'discount_value',
        'coupon',
        'is_featured',
        'is_active',
        'start_date',
        'end_date',
    )
    list_filter = ('discount_type', 'is_featured', 'is_active')
    search_fields = ('title', 'short_description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('products',)