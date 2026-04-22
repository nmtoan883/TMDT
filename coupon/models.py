from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    assigned_user = models.ForeignKey(
        'auth.User',
        related_name='gifted_coupons',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    source_order = models.ForeignKey(
        'orders.Order',
        related_name='gifted_coupons',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    claimed_from = models.ForeignKey(
        'self',
        related_name='claimed_coupons',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    gift_note = models.CharField(max_length=255, blank=True)
    claimable = models.BooleanField(default=False)
    claim_valid_days = models.PositiveIntegerField(default=3)
    public_batch_date = models.DateField(blank=True, null=True)
    public_batch_slot = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

    def meets_min_order_amount(self, amount):
        return amount >= self.min_order_amount

    @property
    def is_personal(self):
        return self.assigned_user_id is not None

    @property
    def is_public_claim_template(self):
        return self.claimable and self.assigned_user_id is None
