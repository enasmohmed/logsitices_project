from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db import models


# Create your models here.


class Owner(models.Model):
    owner = models.OneToOneField(User, related_name='owner_profile', on_delete=models.CASCADE)
    can_view_all_companies = models.BooleanField(default=False)
    total_quantities = models.CharField(max_length=255, blank=True, null=True)
    Total_No_of_Employees = models.CharField(max_length=255, blank=True, null=True)

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
        sund = "Sunday", "Sunday"

    assigned_day = models.CharField(max_length=10, choices=Weekday.choices)
    inbound_entries = models.ManyToManyField('Inbound', related_name='inbound_entries_customuser', blank=True)

    OBD = models.CharField(max_length=255, blank=True, null=True)
    INVOICE = models.CharField(max_length=255, blank=True, null=True)
    PO = models.CharField(max_length=255, blank=True, null=True)

    class SELECTION(models.TextChoices):
        default = "...", "..."
        sur = "Surgical Innovation", "Surgical Innovation"
        pat = "Patient Monitoring", "Patient Monitoring"
        res = "Respiratory Interventions", "Respiratory Interventions"
        ent = "ENT", "ENT"
        neu = "Neurovascular", "Neurovascular"
        end = "Endovenous", "Endovenous"
        cor = "Coronary", "Coronary"
        foc = "FOC", "FOC"
        wm = "WM", "WM"

    OU = models.CharField(max_length=255, choices=SELECTION.choices, default='....')
    Ship_to_Location = models.CharField(max_length=255, blank=True, null=True)
    Shipment_dash = models.CharField(max_length=255, blank=True, null=True)
    PGI_Date = models.CharField(max_length=255, blank=True, null=True)
    Q = models.CharField(max_length=255, blank=True, null=True)
    ASN_Appointment = models.CharField(max_length=255, blank=True, null=True)
    ASN = models.CharField(max_length=255, blank=True, null=True)

    class ASNSTATUSSELECTION(models.TextChoices):
        default = "...", "..."
        rga = "RGA", "RGA"
        deliv = "Delivered", "Delivered"
        app = "Approved", "Approved"
        new = "New", "New"
        re = "Return", "Return"
        re_as = "Re-ASN", "Re-ASN"
        rej = "Rejected", "Rejected"
        iss = "Issue", "Issue"
        not_deliv = "Not Delivered", "Not Delivered"
        under = "Under RGA", "Under RGA"

    ASN_Status = models.CharField(max_length=255, choices=ASNSTATUSSELECTION.choices, default='....')

    class PODSELECTION(models.TextChoices):
        default = "...", "..."
        cn = "CN", "CN"
        pod = "POD", "POD"

    POD = models.CharField(max_length=255, choices=PODSELECTION.choices, default='....')

    class GRNASNSELECTION(models.TextChoices):
        default = "...", "..."
        gr = "GR Issued", "GR Issued"
        nodeliv = "Not Delivered", "Not Delivered"
        phy = "Physically Received", "Physically Received"
        na = "N/A", "N/A"

    GRN_ASN = models.CharField(max_length=255, choices=GRNASNSELECTION.choices, default='....')

    OLD_ASN = models.CharField(max_length=255, blank=True, null=True)
    Date_of_OLD_ASN = models.CharField(max_length=255, blank=True, null=True)
    OLD_ASN_Status = models.CharField(max_length=255, blank=True, null=True)

    class ISSUESELECTION(models.TextChoices):
        default = "...", "..."
        po = "PO Expiry Date", "PO Expiry Date"
        appo = "Appointment canceled from NUPCO", "Appointment canceled from NUPCO"
        asn = "ASN QTY Mismatch", "ASN QTY Mismatch"
        size = "Size of item", "Size of item"
        ship = "Ship to Location", "Ship to Location"
        war = "Warehouse Transfer", "Warehouse Transfer"
        tra = "Transportation issue", "Transportation issue"
        wro = "Wrong/Missing Information", "Wrong/Missing Information"
        sho = "Short Notice Approval from Nupco", "Short Notice Approval from Nupco"
        dis = "Dispatch request before PO Due Date (early)", "Dispatch request before PO Due Date (early)"
        ann = "Annual Cycle Count", "Annual Cycle Count"
        qty = "QTY Issue", "QTY Issue"
        shi = "Shipment closed/not visible on NUPCO portal", "Shipment closed/not visible on NUPCO portal"
        inv = "Invoice Issue", "Invoice Issue"
        poiss = "PO Issue", "PO Issue"
        shel = "Short shelf life of item", "Short shelf life of item"
        nup = "NUPCO Deleted some lines from the ASN", "NUPCO Deleted some lines from the ASN"
        enin = "Eninvoicing Issue", "Eninvoicing Issue"

    Issue = models.CharField(max_length=255, choices=ISSUESELECTION.choices, default='....')
    Remark_1 = models.CharField(max_length=255, blank=True, null=True)
    Remark_2 = models.CharField(max_length=255, blank=True, null=True)

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


class Damage(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='damage_data', on_delete=models.CASCADE)
    total_dash_SKUs_Audited_in_Inventory = models.CharField(max_length=255, blank=True, null=True)
    dash_of_SKUs_with_discripancy = models.CharField(max_length=255, blank=True, null=True)
    Total_QTYs_Damaged_by_WH = models.CharField(max_length=255, blank=True, null=True)
    Number_of_Damaged_during_receiving = models.CharField(max_length=255, blank=True, null=True)
    Total_Damaged_QTYs_Disposed = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class TravelDistance(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='travel_distance_data', on_delete=models.CASCADE)
    Total_no_of_Customers_deliverd = models.CharField(max_length=255, blank=True, null=True)
    Total_no_of_Pallet_deliverd = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Inventory(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='inventory_data', on_delete=models.CASCADE)
    Total_Locations_Audited = models.CharField(max_length=255, blank=True, null=True)
    Total_Locations_with_Incorrect_SKU_and_Qty = models.CharField(max_length=255, blank=True, null=True)
    Total_SKUs_Reconciliation = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class PalletLocationAvailability(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='pallet_location_availability_data',
                                    on_delete=models.CASCADE)
    Total_Storage_Pallet = models.CharField(max_length=255, blank=True, null=True)
    Total_Storage_Bin = models.CharField(max_length=255, blank=True, null=True)
    Total_Storage_pallet_empty = models.CharField(max_length=255, blank=True, null=True)
    Total_Storage_Bin_empty = models.CharField(max_length=255, blank=True, null=True)
    Total_occupied_pallet_location = models.CharField(max_length=255, blank=True, null=True)
    Total_occupied_pallet_locaiton2 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class HSE(models.Model):
    custom_user = models.ForeignKey(CustomUser, related_name='hse_data', on_delete=models.CASCADE)
    Total_Incidents_on_the_side = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)
