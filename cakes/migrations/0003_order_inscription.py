# Generated by Django 4.2.3 on 2023-07-25 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cakes', '0002_shape_price_alter_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='inscription',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]