# Generated by Django 5.0.6 on 2024-06-23 22:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_transaction_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='product',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='store.product'),
            preserve_default=False,
        ),
    ]
