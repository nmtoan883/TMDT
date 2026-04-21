from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path("create/", views.order_create, name="order_create"),
    path("history/", views.order_history, name="order_history"),
    path("tracking/", views.order_tracking, name="order_tracking"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/pay/", views.order_payment, name="order_payment"),
    path("payment_return/", views.payment_return, name="payment_return"),
    path("checkout/", views.checkout, name="checkout"),
    path('payment/sepay/webhook/', views.sepay_webhook, name='sepay_webhook'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]
