# Generated by Django 5.0.6 on 2024-05-28 16:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Capacity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=10)),
                ('total_available_locations_and_accupied', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Inbound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=10)),
                ('number_of_vehicles_daily', models.CharField(blank=True, max_length=255, null=True)),
                ('number_of_pallets', models.CharField(blank=True, max_length=255, null=True)),
                ('shipment_type_bulk', models.CharField(blank=True, max_length=255, null=True)),
                ('shipment_type_mix', models.CharField(blank=True, max_length=255, null=True)),
                ('shipment_type_cold', models.CharField(blank=True, max_length=255, null=True)),
                ('shipment_type_frozen', models.CharField(blank=True, max_length=255, null=True)),
                ('shipment_type_ambient', models.CharField(blank=True, max_length=255, null=True)),
                ('pending_shipments', models.CharField(blank=True, max_length=255, null=True)),
                ('no_of_shipments', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=10)),
                ('last_movement', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Outbound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=10)),
                ('no_of_orders_tender', models.CharField(blank=True, max_length=255, null=True)),
                ('no_of_orders_private', models.CharField(blank=True, max_length=255, null=True)),
                ('no_of_lines', models.CharField(blank=True, max_length=255, null=True)),
                ('total_quantities', models.CharField(blank=True, max_length=255, null=True)),
                ('order_type_bulk', models.CharField(blank=True, max_length=255, null=True)),
                ('order_type_loose', models.CharField(blank=True, max_length=255, null=True)),
                ('pending_orders', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Returns',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField()),
                ('assigned_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Sunday', 'Sunday')], max_length=10)),
                ('no_of_return', models.CharField(blank=True, max_length=255, null=True)),
                ('no_of_lines', models.CharField(blank=True, max_length=255, null=True)),
                ('total_quantities', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_view_all_companies', models.BooleanField(default=False)),
                ('total_quantities', models.CharField(blank=True, max_length=255, null=True)),
                ('Total_No_of_Employees', models.CharField(blank=True, max_length=255, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]