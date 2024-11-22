# Generated by Django 5.0.6 on 2024-07-06 17:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_customuser_is_active_alter_customuser_is_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='HierarchicalGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subgroups', to='accounts.hierarchicalgroup')),
                ('users', models.ManyToManyField(related_name='groups_customer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
