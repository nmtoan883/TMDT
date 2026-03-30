from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # allauth (đăng nhập, đăng ký, quên mật khẩu, Google, Facebook)
    path('accounts/', include('allauth.urls')),

    # Accounts app riêng (profile, register thủ công)
    path('user/', include('accounts.urls', namespace='accounts')),

    # Cart
    path('cart/', include('cart.urls', namespace='cart')),

    # Core shop (phải đặt cuối)
    path('', include('core.urls', namespace='shop')),
    path('coupon/', include('coupon.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
