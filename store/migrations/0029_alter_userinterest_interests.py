# Generated by Django 5.0.6 on 2024-07-24 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_remove_userinterest_interest_userinterest_interests_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinterest',
            name='interests',
            field=models.JSONField(default=list),
        ),
    ]
