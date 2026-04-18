from django.contrib import admin
from .models import PolicyPage, BusinessLicense


@admin.register(PolicyPage)
class PolicyPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'policy_type', 'is_published', 'updated_at')
    list_filter = ('policy_type', 'is_published')
    search_fields = ('title', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(BusinessLicense)
class BusinessLicenseAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'license_number', 'tax_code', 'issue_date', 'is_published', 'updated_at')
    search_fields = ('company_name', 'license_number', 'tax_code')