# Generated by Django 5.0.6 on 2024-06-24 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_review_review_text_review_sentiment'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=100)),
                ('sales_date', models.DateField()),
                ('sales_quantity', models.IntegerField()),
            ],
        ),
    ]
