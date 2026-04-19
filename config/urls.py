from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('user/', include('accounts.urls', namespace='accounts')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('blog/', include('blog.urls')),
    path('', include('legal.urls')),
    path('', include('promotions.urls')),
    path('admin/', include('dasher_admin.urls', namespace='dasher_admin')),
    path('', include('core.urls', namespace='shop')),
    path('coupon/', include('coupon.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
