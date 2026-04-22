from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('voucher/claim/<int:coupon_id>/', views.claim_voucher, name='claim_voucher'),
    path('password/', views.change_password, name='change_password'),
]
