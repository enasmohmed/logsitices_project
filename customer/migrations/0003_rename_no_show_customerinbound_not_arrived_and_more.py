# Generated by Django 5.0.6 on 2024-10-06 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_rename_waiting_for_nupco_action_customerinbound_waiting_for_action_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerinbound',
            old_name='no_show',
            new_name='not_arrived',
        ),
        migrations.RemoveField(
            model_name='customerinbound',
            name='total_shipments_in_asn',
        ),
    ]
