# Generated by Django 5.0.6 on 2024-10-06 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_rename_dash_of_gr_reports_with_discripancy_customerinbound_number_of_gr_reports_with_discripancy_and'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerinventory',
            old_name='Total_Locations_Audited',
            new_name='Total_Locations_match',
        ),
        migrations.RenameField(
            model_name='customerinventory',
            old_name='Total_Locations_with_Incorrect_SKU_and_Qty',
            new_name='Total_Locations_not_match',
        ),
        migrations.RemoveField(
            model_name='customerinventory',
            name='Total_SKUs_Reconciliation',
        ),
    ]