from django.urls import path
from . import views

app_name = 'coupon'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),

    # Nhận kết quả thanh toán
    path('payment_return/', views.payment_return, name='payment_return'),
]