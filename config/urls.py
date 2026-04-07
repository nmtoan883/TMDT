from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('user/', include('accounts.urls', namespace='accounts')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('blog/', include('blog.urls')),
    path('contact/', views.contact_view, name='contact'),
    path('', views.product_list, name='product_list'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('', include('core.urls', namespace='shop')),
    path('coupon/', include('coupon.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
