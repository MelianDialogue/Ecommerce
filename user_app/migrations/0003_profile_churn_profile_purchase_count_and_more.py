# Generated by Django 5.0.6 on 2024-06-23 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0002_profile_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='churn',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='purchase_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='total_spent',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
