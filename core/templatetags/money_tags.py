from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def vnd(value):
    if value in (None, ''):
        amount = Decimal('0')
    else:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return value

    amount = int(amount.quantize(Decimal('1')))
    return f'{amount:,}'.replace(',', '.') + ' đ'
