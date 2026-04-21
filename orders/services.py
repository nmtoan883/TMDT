from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Product


def deduct_stock_for_completed_order(order):
    if order.stock_deducted:
        return

    with transaction.atomic():
        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(
                id__in=order.items.values_list('product_id', flat=True)
            )
        }

        for item in order.items.select_related('product'):
            product = locked_products[item.product_id]
            if product.stock < item.quantity:
                raise ValidationError(
                    f'Sản phẩm "{product.name}" chỉ còn {product.stock} cái, không đủ để hoàn tất đơn.'
                )

        for item in order.items.select_related('product'):
            product = locked_products[item.product_id]
            product.stock -= item.quantity
            product.save(update_fields=['stock'])

        order.stock_deducted = True
        order.save(update_fields=['stock_deducted'])
