from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0006_coupon_claim_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='public_batch_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coupon',
            name='public_batch_slot',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
