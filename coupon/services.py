import secrets
import string
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Coupon


REWARD_MIN_ORDER_AMOUNT = Decimal('2000000')
REWARD_VALID_DAYS = 30
REWARD_TIERS = (
    (Decimal('100000000'), 20),
    (Decimal('50000000'), 15),
    (Decimal('30000000'), 10),
)


def get_reward_discount_percent(order_total):
    order_total = Decimal(str(order_total or 0))
    for threshold, discount_percent in REWARD_TIERS:
        if order_total >= threshold:
            return discount_percent
    return None


def _generate_reward_code(order):
    alphabet = string.ascii_uppercase + string.digits
    while True:
        suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
        code = f'THANK{order.id}{suffix}'
        if not Coupon.objects.filter(code=code).exists():
            return code


def create_reward_coupon_for_order(order):
    if not order.user_id:
        return None

    discount_percent = get_reward_discount_percent(order.get_total_cost())
    if not discount_percent:
        return None

    existing_coupon = Coupon.objects.filter(
        assigned_user=order.user,
        source_order=order,
    ).first()
    if existing_coupon:
        return existing_coupon

    now = timezone.now()
    return Coupon.objects.create(
        code=_generate_reward_code(order),
        discount_percent=discount_percent,
        discount_amount=None,
        min_order_amount=REWARD_MIN_ORDER_AMOUNT,
        valid_from=now,
        valid_to=now + timedelta(days=REWARD_VALID_DAYS),
        active=True,
        assigned_user=order.user,
        source_order=order,
        gift_note=f'Tặng sau khi hoàn tất đơn hàng #{order.id}',
    )
