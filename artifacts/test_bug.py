import os
import django
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from orders.views import order_create
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware

req = RequestFactory().post('/orders/create/', {
    'first_name': 'Test',
    'last_name': '123',
    'email': 'idalia@nmt.io.vn',
    'address': '2 vo oanh',
    'province': 'Thành phố Hồ Chí M',
    'district': 'Quận Bình Thạnh',
    'ward': 'Phường 26',
    'postal_code': '70000',
    'payment_method': 'sepay'
})

SessionMiddleware(lambda r: None).process_request(req)
MessageMiddleware(lambda r: None).process_request(req)
req.session.save()

req.user = User.objects.get(username='admin')
req.session['cart'] = {'1': {'quantity': 1, 'price': '10000.00'}}
req.session['selected_cart_items'] = ['1']
req.session.save()

try:
    res = order_create(req)
    print("STATUS CODE:", res.status_code)
except Exception:
    traceback.print_exc()
