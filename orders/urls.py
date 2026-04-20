from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/payment/sepay/', views.sepay_payment, name='sepay_payment'),
    path('payment/sepay/callback/', views.sepay_callback, name='sepay_callback'),
]
