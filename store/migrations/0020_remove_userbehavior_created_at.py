# Generated by Django 5.0.6 on 2024-06-30 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_userbehavior_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbehavior',
            name='created_at',
        ),
    ]