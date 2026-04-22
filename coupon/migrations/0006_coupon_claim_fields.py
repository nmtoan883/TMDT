from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0005_coupon_assigned_user_source_order_gift_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='claim_valid_days',
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='coupon',
            name='claimable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coupon',
            name='claimed_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claimed_coupons', to='coupon.coupon'),
        ),
    ]
