# Generated by Django 5.0.6 on 2024-10-06 21:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_rename_total_locations_audited_customerinventory_total_locations_match_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customeroutbound',
            old_name='number_of_orders_that_are_delivered_today',
            new_name='pending_pick_orders',
        ),
        migrations.RenameField(
            model_name='customeroutbound',
            old_name='order_received_from_npco',
            new_name='piked_order',
        ),
        migrations.RenameField(
            model_name='customeroutbound',
            old_name='pending_orders',
            new_name='released_order',
        ),
        migrations.CreateModel(
            name='CustomerTransportationOutbound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=20)),
                ('Total_no_of_Customers_deliverd', models.IntegerField(blank=True, null=True)),
                ('Total_no_of_Pallet_deliverd', models.IntegerField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transportation_outbound', to='customer.customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerWHOutbound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=20)),
                ('released_order', models.IntegerField(blank=True, null=True)),
                ('pending_pick_orders', models.IntegerField(blank=True, null=True)),
                ('number_of_order_not_yet_picked', models.IntegerField(blank=True, null=True)),
                ('number_of_orders_picked_but_not_yet_ready_for_disptch_in_progress', models.IntegerField(blank=True, null=True)),
                ('number_of_orders_waiting_for_qc', models.IntegerField(blank=True, null=True)),
                ('number_of_orders_that_are_ready_for_dispatch', models.IntegerField(blank=True, null=True)),
                ('piked_order', models.IntegerField(blank=True, null=True)),
                ('justification_for_the_delay_order_by_order', models.IntegerField(blank=True, null=True)),
                ('total_skus_picked', models.IntegerField(blank=True, null=True)),
                ('total_dash_of_SKU_discripancy_in_Order', models.IntegerField(blank=True, null=True)),
                ('number_of_PODs_collected_on_time', models.IntegerField(blank=True, null=True)),
                ('number_of_PODs_collected_Late', models.IntegerField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wh_outbounds', to='customer.customer')),
            ],
        ),
    ]