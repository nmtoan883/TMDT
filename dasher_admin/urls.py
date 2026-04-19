from django.urls import path
from . import views

app_name = 'dasher_admin'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/categories/', views.blog_category_list, name='blog_category_list'),
]
