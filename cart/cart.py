from decimal import Decimal
from django.conf import settings
from core.models import Product
from coupon.models import Coupon


class Cart:
    SELECTED_ITEMS_SESSION_KEY = 'selected_cart_items'

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self._remove_from_selected(product_id)
            self.save()

    def __iter__(self):
        yield from self.get_items()

    def get_items(self, product_ids=None):
        product_ids = [str(pid) for pid in (product_ids or self.cart.keys()) if str(pid) in self.cart]
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for product_id in product_ids:
            item = cart.get(str(product_id))
            if not item or 'product' not in item:
                continue
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self, product_ids=None):
        items = self.get_items(product_ids) if product_ids is not None else self.cart.values()
        return sum(Decimal(item['price']) * item['quantity'] for item in items)

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.pop(self.SELECTED_ITEMS_SESSION_KEY, None)
        self.save()

    def get_selected_product_ids(self):
        selected = self.session.get(self.SELECTED_ITEMS_SESSION_KEY)
        if not selected:
            return list(self.cart.keys())
        return [pid for pid in selected if pid in self.cart]

    def set_selected_product_ids(self, product_ids):
        selected = [str(pid) for pid in product_ids if str(pid) in self.cart]
        self.session[self.SELECTED_ITEMS_SESSION_KEY] = selected
        self.save()

    def get_selected_items(self):
        return list(self.get_items(self.get_selected_product_ids()))

    def _remove_from_selected(self, product_id):
        selected = self.session.get(self.SELECTED_ITEMS_SESSION_KEY)
        if not selected:
            return
        updated = [pid for pid in selected if pid != str(product_id)]
        self.session[self.SELECTED_ITEMS_SESSION_KEY] = updated

    def get_coupon(self):
        coupon_id = self.session.get('coupon_id')
        if coupon_id:
            try:
                return Coupon.objects.get(id=coupon_id, active=True)
            except Coupon.DoesNotExist:
                return None
        return None

    def get_discount(self, product_ids=None):
        coupon = self.get_coupon()
        if coupon:
            return (coupon.discount / Decimal('100')) * self.get_total_price(product_ids)
        return Decimal('0')

    def get_total_price_after_discount(self, product_ids=None):
        return self.get_total_price(product_ids) - self.get_discount(product_ids)
