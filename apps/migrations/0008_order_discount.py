# Generated migration for adding discount fields to Order
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_vote_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
