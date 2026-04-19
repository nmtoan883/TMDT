from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('khuyen-mai/', views.promotion_list, name='promotion_list'),
    path('khuyen-mai/<slug:slug>/', views.promotion_detail, name='promotion_detail'),
]