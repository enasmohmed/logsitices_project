from django.conf import settings
from django.db import models


# Create your models here.


class Customer(models.Model):
    name_company = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_company


class CustomerInbound(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)

    total_shipments_in_asn = models.IntegerField(blank=True, null=True)
    arrived = models.IntegerField(blank=True, null=True)
    no_show = models.IntegerField(blank=True, null=True)
    received_completely = models.IntegerField(blank=True, null=True)
    rejected_completely = models.IntegerField(blank=True, null=True)
    received_partially = models.IntegerField(blank=True, null=True)
    under_tamer_inspection = models.IntegerField(blank=True, null=True)
    waiting_for_mod_inspection = models.IntegerField(blank=True, null=True)
    waiting_for_NUPCO_action = models.IntegerField(blank=True, null=True)
    total_dash_of_GR_reports_shared = models.IntegerField(blank=True, null=True)
    dash_of_GR_reports_with_discripancy = models.IntegerField(blank=True, null=True)
    total_SKUS_received = models.IntegerField(blank=True, null=True)
    dash_of_skus_damaged_during_receiving = models.IntegerField(blank=True, null=True)
    total_received_with_putaway = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerOutbound(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)

    order_received_from_npco = models.IntegerField(blank=True, null=True)
    pending_orders = models.IntegerField(blank=True, null=True)
    number_of_order_not_yet_picked = models.IntegerField(blank=True, null=True)
    number_of_orders_picked_but_not_yet_ready_for_disptch_in_progress = models.IntegerField(blank=True, null=True)
    number_of_orders_waiting_for_mod_qc = models.IntegerField(blank=True, null=True)
    number_of_orders_that_are_ready_for_dispatch = models.IntegerField(blank=True, null=True)
    number_of_orders_that_are_delivered_today = models.IntegerField(blank=True, null=True)
    justification_for_the_delay_order_by_order = models.IntegerField(blank=True, null=True)
    total_skus_picked = models.IntegerField(blank=True, null=True)
    total_dash_of_SKU_discripancy_in_Order = models.IntegerField(blank=True, null=True)
    number_of_PODs_collected_on_time = models.IntegerField(blank=True, null=True)
    number_of_PODs_collected_Late = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerReturns(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)

    total_orders_items_returned = models.IntegerField(blank=True, null=True)
    number_of_return_items_orders_updated_on_time = models.IntegerField(blank=True, null=True)
    number_of_return_items_orders_updated_late = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerExpiry(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)
    total_SKUs_expired = models.IntegerField(blank=True, null=True)
    total_expired_SKUS_disposed = models.IntegerField(blank=True, null=True)
    nearly_expired_1_to_3_months = models.IntegerField(blank=True, null=True)
    nearly_expired_3_to_6_months = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerDamage(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)
    Total_QTYs_Damaged_by_WH = models.IntegerField(blank=True, null=True)
    Number_of_Damaged_during_receiving = models.IntegerField(blank=True, null=True)
    Total_Damaged_QTYs_Disposed = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerTravelDistance(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)

    Total_no_of_Customers_deliverd = models.IntegerField(blank=True, null=True)
    Total_no_of_Pallet_deliverd = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerInventory(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)
    Total_Locations_Audited = models.IntegerField(blank=True, null=True)
    Total_Locations_with_Incorrect_SKU_and_Qty = models.IntegerField(blank=True, null=True)
    Total_SKUs_Reconciliation = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerPalletLocationAvailability(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)
    Total_Storage_Pallet = models.IntegerField(blank=True, null=True)
    Total_Storage_Bin = models.IntegerField(blank=True, null=True)
    Total_Storage_pallet_empty = models.IntegerField(blank=True, null=True)
    Total_Storage_Bin_empty = models.IntegerField(blank=True, null=True)
    Total_occupied_pallet_location = models.IntegerField(blank=True, null=True)
    Total_occupied_Bin_location = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class CustomerHSE(models.Model):
    time = models.DateField()

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=20, choices=Weekday.choices)
    Total_Incidents_on_the_side = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)
