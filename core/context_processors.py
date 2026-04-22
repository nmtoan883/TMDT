from .models import Category, UserNotification
from django.utils import timezone
from accounts.views import (
    _active_public_slots,
    _annotate_public_voucher_groups_for_user,
    _get_daily_public_vouchers,
    _group_public_vouchers,
    _next_public_voucher_slot_label,
)

def categories(request):
    context = {'categories': Category.objects.all()}

    if request.user.is_authenticated:
        notifications = UserNotification.objects.filter(user=request.user)
        context.update({
            'user_notifications': notifications[:5],
            'unread_notification_count': notifications.filter(is_read=False).count(),
        })
    else:
        context.update({
            'user_notifications': [],
            'unread_notification_count': 0,
        })

    now = timezone.now()
    public_voucher_groups = _group_public_vouchers(_get_daily_public_vouchers(request.user, now))
    context.update({
        'floating_public_vouchers': _annotate_public_voucher_groups_for_user(public_voucher_groups, request.user, now),
        'floating_can_claim_public_vouchers': bool(_active_public_slots(now)),
        'floating_next_public_voucher_slot_label': _next_public_voucher_slot_label(now),
    })

    return context
