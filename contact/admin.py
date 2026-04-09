from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    list_filter = ['subject', 'created_at']