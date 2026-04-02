from django.urls import path
from .views import home, cart

urlpatterns = [
    path('', home, name='home'),
    path('cart/', cart, name='cart'),
]