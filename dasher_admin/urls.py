from django.urls import path
from . import views

app_name = 'dasher_admin'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/add/', views.blog_add, name='blog_add'),
    path('blog/edit/<int:pk>/', views.blog_edit, name='blog_edit'),
    path('blog/delete/<int:pk>/', views.blog_delete, name='blog_delete'),
    # Blog Categories
    path('blog/categories/', views.blog_category_list, name='blog_category_list'),
    path('blog/categories/add/', views.blog_category_add, name='blog_category_add'),
    path('blog/categories/edit/<int:pk>/', views.blog_category_edit, name='blog_category_edit'),
    path('blog/categories/delete/<int:pk>/', views.blog_category_delete, name='blog_category_delete'),

    # Accounts / Customers
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/add/', views.account_add, name='account_add'),
    path('accounts/edit/<int:pk>/', views.account_edit, name='account_edit'),
    path('accounts/delete/<int:pk>/', views.account_delete, name='account_delete'),

    # Legal
    path('legal/policies/', views.legal_policy_list, name='legal_policy_list'),
    path('legal/policies/add/', views.legal_policy_add, name='legal_policy_add'),
    path('legal/policies/edit/<int:pk>/', views.legal_policy_edit, name='legal_policy_edit'),
    path('legal/policies/delete/<int:pk>/', views.legal_policy_delete, name='legal_policy_delete'),
    path('legal/licenses/', views.legal_license_list, name='legal_license_list'),
    path('legal/licenses/add/', views.legal_license_add, name='legal_license_add'),
    path('legal/licenses/edit/<int:pk>/', views.legal_license_edit, name='legal_license_edit'),
    path('legal/licenses/delete/<int:pk>/', views.legal_license_delete, name='legal_license_delete'),
]
