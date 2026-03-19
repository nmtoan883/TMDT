from django.urls import path
from .views import apply_coupon, remove_coupon

app_name = 'coupon'

urlpatterns = [
    path('apply/', apply_coupon, name='apply'),
    path('remove/', remove_coupon, name='remove'),
]