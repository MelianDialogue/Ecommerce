# Generated by Django 5.0.6 on 2024-06-30 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_product_social_media_score_socialmediainteraction'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='supply_chain_forecast',
            field=models.TextField(blank=True, null=True),
        ),
    ]
