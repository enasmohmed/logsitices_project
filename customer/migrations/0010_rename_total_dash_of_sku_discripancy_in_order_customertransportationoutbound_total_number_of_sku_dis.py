# Generated by Django 5.0.6 on 2024-10-08 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0009_rename_dash_of_skus_damaged_during_receiving_customerinbound_number_of_skus_damaged_during_receiving'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customertransportationoutbound',
            old_name='total_dash_of_SKU_discripancy_in_Order',
            new_name='total_number_of_SKU_discripancy_in_Order',
        ),
    ]
