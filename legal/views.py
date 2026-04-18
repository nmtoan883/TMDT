from django.shortcuts import render, get_object_or_404
from .models import PolicyPage, BusinessLicense


def policy_detail(request, slug):
    page = get_object_or_404(PolicyPage, slug=slug, is_published=True)
    return render(request, 'legal/policy_detail.html', {'page': page})


def business_license_detail(request):
    license_obj = BusinessLicense.objects.filter(is_published=True).first()
    return render(request, 'legal/business_license.html', {'license_obj': license_obj})