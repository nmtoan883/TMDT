from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'shop'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='shop:product_list', permanent=False)),
    path('home/', views.product_list, name='product_list'),
    path('hot-deals/', views.hotdeal_list, name='hotdeal_list'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),

    path('wishlist/', views.wishlist_list, name='wishlist_list'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('create/', views.product_create, name='product_create'),
    path('contact/', views.contact_view, name='contact'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
]
