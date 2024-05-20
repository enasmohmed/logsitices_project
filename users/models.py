from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db import models


# Create your models here.


class Owner(models.Model):
    owner = models.OneToOneField(User, related_name='owner_profile', on_delete=models.CASCADE)
    can_view_all_companies = models.BooleanField(default=False)
    total_quantities = models.CharField(max_length=255)

    # Add other fields related to admin permissions

    def __str__(self):
        return self.owner.username


class Company(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='company_employees', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='customuser_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions')

    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sun = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    inbound_entries = models.ManyToManyField('Inbound', related_name='inbound_entries_customuser', blank=True)

    # inbound = models.ForeignKey(Inbound, related_name='user_inbound', on_delete=models.CASCADE, blank=True, null=True)
    # inbound_data = models.ManyToManyField('Inbound', related_name='inbound_data_custom')

    def __str__(self):
        return self.username


class Inbound(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='inbound_data', on_delete=models.CASCADE)
    total_shipments_in_asn = models.CharField(max_length=255, blank=True, null=True)
    arrived = models.CharField(max_length=255, blank=True, null=True)
    no_show = models.CharField(max_length=255, blank=True, null=True)
    received_completely = models.CharField(max_length=255, blank=True, null=True)
    regected_completely = models.CharField(max_length=255, blank=True, null=True)
    received_partially = models.CharField(max_length=255, blank=True, null=True)
    under_tamer_inspection = models.CharField(max_length=255, blank=True, null=True)
    waiting_for_mod_inspection = models.CharField(max_length=255, blank=True, null=True)
    waiting_for_NUPCO_action = models.CharField(max_length=255, blank=True, null=True)
    total_dash_of_GR_reports_shared = models.CharField(max_length=255, blank=True, null=True)
    dash_of_GR_reports_with_discripancy = models.CharField(max_length=255, blank=True, null=True)
    total_SKUS_received = models.CharField(max_length=255, blank=True, null=True)
    dash_of_skus_damaged_during_receiving = models.CharField(max_length=255, blank=True, null=True)
    total_received_with_putaway = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Outbound(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='outbound_data', on_delete=models.CASCADE)
    order_received_from_npco = models.CharField(max_length=255, blank=True, null=True)
    pending_orders = models.CharField(max_length=255, blank=True, null=True)
    number_of_order_not_yet_picked = models.CharField(max_length=255, blank=True, null=True)
    number_of_orders_picked_but_not_yet_ready_for_disptch_in_progress = models.CharField(max_length=255, blank=True,
                                                                                         null=True)
    number_of_orders_waiting_for_mod_qc = models.CharField(max_length=255, blank=True, null=True)
    number_of_orders_that_are_ready_for_dispatch = models.CharField(max_length=255, blank=True, null=True)
    number_of_orders_that_are_delivered_today = models.CharField(max_length=255, blank=True, null=True)
    justification_for_the_delay_order_by_order = models.CharField(max_length=255, blank=True, null=True)
    total_skus_picked = models.CharField(max_length=255, blank=True, null=True)
    total_dash_of_SKU_discripancy_in_Order = models.CharField(max_length=255, blank=True, null=True)
    number_of_PODs_collected_on_time = models.CharField(max_length=255, blank=True, null=True)
    number_of_PODs_collected_Late = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Returns(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='return_data', on_delete=models.CASCADE)
    total_orders_items_returned = models.CharField(max_length=255, blank=True, null=True)
    number_of_return_items_orders_updated_on_time = models.CharField(max_length=255, blank=True, null=True)
    number_of_return_items_orders_updated_late = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Expiry(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='expiry_data', on_delete=models.CASCADE)
    total_SKUs_expired = models.CharField(max_length=255, blank=True, null=True)
    total_expired_SKUS_disposed = models.CharField(max_length=255, blank=True, null=True)
    nearly_expired_1_to_3_months = models.CharField(max_length=255, blank=True, null=True)
    nearly_expired_3_to_6_months = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)
