from django.urls import path
from . import views

app_name = 'dasher_admin'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/add/', views.blog_add, name='blog_add'),
    path('blog/edit/<int:pk>/', views.blog_edit, name='blog_edit'),
    path('blog/delete/<int:pk>/', views.blog_delete, name='blog_delete'),
    path('blog/categories/', views.blog_category_list, name='blog_category_list'),
    path('blog/categories/add/', views.blog_category_add, name='blog_category_add'),
    path('blog/categories/edit/<int:pk>/', views.blog_category_edit, name='blog_category_edit'),
    path('blog/categories/delete/<int:pk>/', views.blog_category_delete, name='blog_category_delete'),
]
