from core.models import Product

class Wishlist:
    def __init__(self, request):
        self.session = request.session
        wishlist = self.session.get('wishlist', [])
        self.wishlist = wishlist

    def add(self, product_id):
        product_id = int(product_id)
        if product_id not in self.wishlist:
            self.wishlist.insert(0, product_id)
            self.session['wishlist'] = self.wishlist
            self.session.modified = True

    def remove(self, product_id):
        product_id = int(product_id)
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            self.session['wishlist'] = self.wishlist
            self.session.modified = True

    def get_products(self):
        wishlist_ids = [int(pid) for pid in self.wishlist]
        products = list(Product.objects.filter(id__in=wishlist_ids, available=True))
        products.sort(key=lambda x: wishlist_ids.index(x.id))
        return products

    def __contains__(self, product_id):
        return int(product_id) in [int(pid) for pid in self.wishlist]