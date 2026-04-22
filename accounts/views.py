from django.contrib import messages
import random
import secrets
import string
from datetime import timedelta

from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from coupon.models import Coupon

from .forms import CustomerProfileForm, UserRegistrationForm, UserUpdateForm
from .models import CustomerProfile


DAILY_PUBLIC_VOUCHER_LIMIT = 50
PUBLIC_VOUCHER_SLOTS = (
    ('noon', 12, '12:00'),
    ('evening', 21, '21:00'),
)


def _voucher_dashboard_url():
    return reverse('accounts:dashboard') + '?tab=vouchers'


def _generate_claimed_coupon_code():
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = 'CLAIM' + ''.join(secrets.choice(alphabet) for _ in range(10))
        if not Coupon.objects.filter(code=code).exists():
            return code


def _active_public_slots(now):
    current_hour = timezone.localtime(now).hour
    return [
        (slot, label)
        for slot, hour, label in PUBLIC_VOUCHER_SLOTS
        if current_hour >= hour
    ]


def _ensure_public_voucher_batch(now, slot):
    today = timezone.localdate(now)
    if Coupon.objects.filter(
        public_batch_date=today,
        public_batch_slot=slot,
    ).exists():
        return

    vouchers = list(Coupon.objects.filter(
        claimable=True,
        assigned_user__isnull=True,
        active=True,
        public_batch_date__isnull=True,
        public_batch_slot='',
    ))

    seed = f'{today.isoformat()}:{slot}'
    rng = random.Random(seed)
    rng.shuffle(vouchers)
    selected_ids = [voucher.id for voucher in vouchers[:DAILY_PUBLIC_VOUCHER_LIMIT]]
    if selected_ids:
        Coupon.objects.filter(id__in=selected_ids).update(
            public_batch_date=today,
            public_batch_slot=slot,
        )


def _ensure_active_public_voucher_batches(now):
    for slot, _label in _active_public_slots(now):
        _ensure_public_voucher_batch(now, slot)


def _get_daily_public_vouchers(user, now):
    active_slots = _active_public_slots(now)
    today = timezone.localdate(now)
    slot_names = ['manual']

    if active_slots:
        _ensure_active_public_voucher_batches(now)
        slot_names += [slot for slot, _label in active_slots]

    return list(Coupon.objects.filter(
        claimable=True,
        assigned_user__isnull=True,
        active=True,
        public_batch_date=today,
        public_batch_slot__in=slot_names,
    ).order_by('public_batch_slot', 'id'))


def _next_public_voucher_slot_label(now):
    current_hour = timezone.localtime(now).hour
    for _slot, hour, label in PUBLIC_VOUCHER_SLOTS:
        if current_hour < hour:
            return label
    return None


def _today_bounds(now):
    start = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


def _has_claimed_public_voucher_today(user, now):
    start, end = _today_bounds(now)
    return Coupon.objects.filter(
        assigned_user=user,
        claimed_from__isnull=False,
        valid_from__gte=start,
        valid_from__lt=end,
    ).exists()


def register(request):
    if request.user.is_authenticated:
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Chào mừng {new_user.username}! Tài khoản của bạn đã được tạo thành công.')
            return redirect('shop:product_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if not profile.province and profile.city:
        profile.province = profile.city
        profile.save(update_fields=['province'])

    is_editing = request.GET.get('edit') == '1'
    active_tab = 'vouchers' if request.GET.get('tab') == 'vouchers' and not is_editing else 'profile'

    if request.method == 'POST':
        is_editing = True
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            saved_profile = profile_form.save(commit=False)
            saved_profile.city = saved_profile.province
            saved_profile.save()
            messages.success(request, 'Thông tin tài khoản đã được cập nhật.')
            return redirect('accounts:dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=profile)

    now = timezone.now()
    public_vouchers = _get_daily_public_vouchers(request.user, now)
    claimed_public_voucher_today = _has_claimed_public_voucher_today(request.user, now)
    can_claim_public_vouchers = bool(_active_public_slots(now))
    user_vouchers = Coupon.objects.filter(
        assigned_user=request.user,
        active=True,
    ).order_by('-valid_to', '-id')

    return render(
        request,
        'accounts/dashboard.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile,
            'is_editing': is_editing,
            'active_tab': active_tab,
            'public_vouchers': public_vouchers,
            'can_claim_public_vouchers': can_claim_public_vouchers,
            'claimed_public_voucher_today': claimed_public_voucher_today,
            'next_public_voucher_slot_label': _next_public_voucher_slot_label(now),
            'available_vouchers': user_vouchers.filter(valid_from__lte=now, valid_to__gte=now),
            'expired_vouchers': user_vouchers.filter(valid_to__lt=now)[:5],
        },
    )


@login_required
@require_POST
def claim_voucher(request, coupon_id):
    now = timezone.now()
    daily_coupon_ids = {coupon.id for coupon in _get_daily_public_vouchers(request.user, now)}
    if not _active_public_slots(now) and coupon_id not in daily_coupon_ids:
        messages.warning(request, 'Voucher công khai sẽ mở claim từ 12:00 và 21:00 mỗi ngày.')
        return redirect(_voucher_dashboard_url())

    if _has_claimed_public_voucher_today(request.user, now):
        messages.warning(request, 'Mỗi tài khoản chỉ được nhận 1 voucher từ kho chung mỗi ngày.')
        return redirect(_voucher_dashboard_url())

    if coupon_id not in daily_coupon_ids:
        messages.warning(request, 'Voucher này không nằm trong danh sách mở claim hôm nay.')
        return redirect(_voucher_dashboard_url())

    with transaction.atomic():
        source_coupon = get_object_or_404(
            Coupon.objects.select_for_update(),
            id=coupon_id,
            claimable=True,
            assigned_user__isnull=True,
            active=True,
        )
        valid_days = source_coupon.claim_valid_days or 3
        Coupon.objects.create(
            code=_generate_claimed_coupon_code(),
            discount_percent=source_coupon.discount_percent,
            discount_amount=source_coupon.discount_amount,
            min_order_amount=source_coupon.min_order_amount,
            valid_from=now,
            valid_to=now + timedelta(days=valid_days),
            active=True,
            assigned_user=request.user,
            claimed_from=source_coupon,
            gift_note=f'Nhận từ voucher công khai, hiệu lực {valid_days} ngày.',
        )
        source_coupon.active = False
        source_coupon.claimable = False
        source_coupon.save(update_fields=['active', 'claimable'])

    messages.success(request, f'Bạn đã nhận voucher giảm {source_coupon.discount_percent}% thành công.')
    return redirect(_voucher_dashboard_url())


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Mật khẩu đã được cập nhật.')
            return redirect('accounts:dashboard')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
