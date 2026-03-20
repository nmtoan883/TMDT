from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'active', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['active', 'created_at']
    search_fields = ['title', 'content']