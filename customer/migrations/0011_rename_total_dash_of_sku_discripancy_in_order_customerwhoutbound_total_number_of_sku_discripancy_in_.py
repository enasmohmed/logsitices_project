# Generated by Django 5.0.6 on 2024-10-08 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_rename_total_dash_of_sku_discripancy_in_order_customertransportationoutbound_total_number_of_sku_dis'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerwhoutbound',
            old_name='total_dash_of_SKU_discripancy_in_Order',
            new_name='total_number_of_SKU_discripancy_in_Order',
        ),
    ]
