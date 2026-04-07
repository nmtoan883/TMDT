from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.blog_search, name='blog_search'),
    path('category/<slug:slug>/', views.blog_by_category, name='blog_by_category'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]