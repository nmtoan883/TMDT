from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# Ensure only staff (Admins) can see dashboard
@staff_member_required
def index(request):
    return render(request, 'dasher_admin/index.html')
