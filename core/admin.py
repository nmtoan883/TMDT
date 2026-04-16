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
    list_display = ['name', 'slug', 'price', 'old_price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}

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
