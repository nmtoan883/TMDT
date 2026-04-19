from django.contrib import admin
from django.utils.html import mark_safe
from .models import Category, Product, Review, Contact, Policy, Wishlist, ContactMessage, ContactInfo

admin.site.register(Wishlist)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'category_image']
    prepopulated_fields = {'slug': ('name',)}

    def category_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:50px; max-width:100px; object-fit:contain;" />')
        return '(No image)'
    category_image.short_description = 'Image'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'slug', 'price', 'old_price', 'stock', 'available',
        'is_hotdeal', 'hotdeal_start', 'hotdeal_end', 'created', 'updated'
    ]
    list_filter = ['available', 'is_hotdeal', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available', 'is_hotdeal']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'brand', 'category__name']
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'slug', 'brand', 'image', 'description')
        }),
        ('Giá và kho', {
            'fields': ('price', 'old_price', 'stock', 'available')
        }),
        ('Hot Deal', {
            'fields': ('is_hotdeal', 'hotdeal_start', 'hotdeal_end'),
            'description': 'Bật Hot Deal và chọn thời gian hiệu lực để hiển thị ở trang chủ.'
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created', 'image']
    list_filter = ['rating', 'created']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created']

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'policy_type']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'subject')
