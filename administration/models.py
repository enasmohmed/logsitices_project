from django.conf import settings
from django.db import models


# Create your models here.

class AdminData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_quantities = models.IntegerField(blank=True, null=True)
    total_no_of_employees = models.IntegerField(blank=True, null=True)
    hc_business = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.hc_business}'


class Inbound(models.Model):
    time = models.DateField()
    admin_data = models.ForeignKey(AdminData, on_delete=models.CASCADE, default=1)

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    number_of_vehicles_daily = models.IntegerField(blank=True, null=True)
    number_of_pallets = models.IntegerField(blank=True, null=True)
    bulk = models.IntegerField(blank=True, null=True)
    mix = models.IntegerField(blank=True, null=True)
    cold = models.IntegerField(blank=True, null=True)
    frozen = models.IntegerField(blank=True, null=True)
    ambient = models.IntegerField(blank=True, null=True)
    pending_shipments = models.IntegerField(blank=True, null=True)
    no_of_shipments = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Outbound(models.Model):
    time = models.DateField()
    admin_data = models.ForeignKey(AdminData, on_delete=models.CASCADE, default=1)

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    tender = models.IntegerField(blank=True, null=True)
    private = models.IntegerField(blank=True, null=True)
    lines = models.IntegerField(blank=True, null=True)
    total_quantities = models.IntegerField(blank=True, null=True)
    bulk = models.IntegerField(blank=True, null=True)
    loose = models.IntegerField(blank=True, null=True)
    pending_orders = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Returns(models.Model):
    time = models.DateField()
    admin_data = models.ForeignKey(AdminData, on_delete=models.CASCADE, default=1)

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    no_of_return = models.IntegerField(blank=True, null=True)
    no_of_lines = models.IntegerField(blank=True, null=True)
    total_quantities = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Capacity(models.Model):
    time = models.DateField()
    admin_data = models.ForeignKey(AdminData, on_delete=models.CASCADE, default=1)

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    total_available_locations_and_accupied = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Inventory(models.Model):
    time = models.DateField()
    admin_data = models.ForeignKey(AdminData, on_delete=models.CASCADE, default=1)

    class Weekday(models.TextChoices):
        mon = "Monday", "Monday"
        tue = "Tuesday", "Tuesday"
        wed = "Wednesday", "Wednesday"
        thu = "Thursday", "Thursday"
        fri = "Friday", "Friday"
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    last_movement = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)
