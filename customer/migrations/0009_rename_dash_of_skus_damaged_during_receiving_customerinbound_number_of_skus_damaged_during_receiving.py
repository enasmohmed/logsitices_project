# Generated by Django 5.0.6 on 2024-10-08 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0008_rename_total_no_of_customers_deliverd_customertransportationoutbound_justification_for_the_delay_ord'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerinbound',
            old_name='dash_of_skus_damaged_during_receiving',
            new_name='number_of_skus_damaged_during_receiving',
        ),
    ]
