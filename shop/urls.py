from django.urls import path
from .views import home, cart, contact

urlpatterns = [
    path('', home, name='home'),
    path('cart/', cart, name='cart'),
    path('contact/', contact, name='contact'),
]