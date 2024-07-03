from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser
from administration.models import AdminInventory, AdminCapacity, AdminReturns, AdminOutbound, AdminInbound, AdminData
from customer.models import CustomerHSE, CustomerPalletLocationAvailability, CustomerInventory, CustomerTravelDistance, \
    CustomerDamage, CustomerExpiry, CustomerReturns, CustomerOutbound, CustomerInbound, Customer, EmployeeProfile


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_approved = False  # الحساب غير مفعل افتراضياً
        user.is_active = False  # الحساب غير نشط افتراضياً
        if user.role in ['employee', 'admin', 'customer']:
            user.is_staff = True
            user.is_active = True
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']


class DateInput(forms.DateInput):
    input_type = 'date'


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name_company']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.groups.filter(name='Employee').exists():
                # Get company name for Employee users
                company = EmployeeProfile.objects.filter(user=user).first().company
            elif user.groups.filter(name='Customer').exists():
                # Get company name for Customer users
                company = Customer.objects.filter(employees__user=user).first()

            if company:
                self.fields['name_company'].initial = company.name_company
                self.fields['name_company'].disabled = True  # Make the field disabled

    # Optional: If `name_company` is not a model field, handle it separately as needed.


class CustomerInboundForm(forms.ModelForm):
    class Meta:
        model = CustomerInbound
        fields = ['time', 'assigned_day', 'total_shipments_in_asn', 'arrived', 'no_show', 'received_completely',
                  'rejected_completely', 'received_partially', 'under_tamer_inspection', 'waiting_for_inspection',
                  'waiting_for_action', 'total_dash_of_GR_reports_shared', 'dash_of_GR_reports_with_discripancy',
                  'total_SKUS_received', 'dash_of_skus_damaged_during_receiving', 'total_received_with_putaway']
        widgets = {
            'time': DateInput(),
        }


class CustomerOutboundForm(forms.ModelForm):
    class Meta:
        model = CustomerOutbound
        fields = ['time', 'assigned_day', 'order_received_from_npco', 'pending_orders',
                  'number_of_order_not_yet_picked', 'number_of_orders_picked_but_not_yet_ready_for_disptch_in_progress',
                  'number_of_orders_waiting_for_qc', 'number_of_orders_that_are_ready_for_dispatch',
                  'number_of_orders_that_are_delivered_today', 'justification_for_the_delay_order_by_order',
                  'total_skus_picked', 'total_dash_of_SKU_discripancy_in_Order', 'number_of_PODs_collected_on_time',
                  'number_of_PODs_collected_Late']
        widgets = {
            'time': DateInput(),
        }


class CustomerReturnsForm(forms.ModelForm):
    class Meta:
        model = CustomerReturns
        fields = ['time', 'assigned_day', 'total_orders_items_returned',
                  'number_of_return_items_orders_updated_on_time', 'number_of_return_items_orders_updated_late']
        widgets = {
            'time': DateInput(),
        }


class CustomerExpiryForm(forms.ModelForm):
    class Meta:
        model = CustomerExpiry
        fields = ['time', 'assigned_day', 'total_SKUs_expired', 'total_expired_SKUS_disposed',
                  'nearly_expired_1_to_3_months', 'nearly_expired_3_to_6_months']
        widgets = {
            'time': DateInput(),
        }


class CustomerDamageForm(forms.ModelForm):
    class Meta:
        model = CustomerDamage
        fields = ['time', 'assigned_day', 'Total_QTYs_Damaged_by_WH', 'Number_of_Damaged_during_receiving',
                  'Total_Damaged_QTYs_Disposed']
        widgets = {
            'time': DateInput(),
        }


class CustomerTravelDistanceForm(forms.ModelForm):
    class Meta:
        model = CustomerTravelDistance
        fields = ['time', 'assigned_day', 'Total_no_of_Customers_deliverd', 'Total_no_of_Pallet_deliverd']
        widgets = {
            'time': DateInput(),
        }


class CustomerInventoryForm(forms.ModelForm):
    class Meta:
        model = CustomerInventory
        fields = ['time', 'assigned_day', 'Total_Locations_Audited', 'Total_Locations_with_Incorrect_SKU_and_Qty',
                  'Total_SKUs_Reconciliation']
        widgets = {
            'time': DateInput(),
        }


class CustomerPalletLocationAvailabilityForm(forms.ModelForm):
    class Meta:
        model = CustomerPalletLocationAvailability
        fields = ['time', 'assigned_day', 'Total_Storage_Pallet', 'Total_Storage_Bin', 'Total_Storage_pallet_empty',
                  'Total_Storage_Bin_empty', 'Total_occupied_pallet_location', 'Total_occupied_Bin_location']
        widgets = {
            'time': DateInput(),
        }


class CustomerHSEForm(forms.ModelForm):
    class Meta:
        model = CustomerHSE
        fields = ['time', 'assigned_day', 'Total_Incidents_on_the_side']
        widgets = {
            'time': DateInput(),
        }


class AdminDataForm(forms.ModelForm):
    class Meta:
        model = AdminData
        fields = ['user', 'total_quantities', 'total_no_of_employees', 'hc_business']
        # widgets = {
        #     'employees': forms.CheckboxSelectMultiple,
        # }


class AdminInboundForm(forms.ModelForm):
    class Meta:
        model = AdminInbound
        fields = ['time', 'assigned_day', 'number_of_vehicles_daily', 'number_of_pallets', 'bulk', 'mix', 'cold',
                  'frozen', 'ambient', 'pending_shipments', 'no_of_shipments']
        widgets = {
            'time': DateInput(),
        }


class AdminOutboundForm(forms.ModelForm):
    class Meta:
        model = AdminOutbound
        fields = ['time', 'assigned_day', 'tender', 'private', 'lines', 'total_quantities', 'bulk', 'loose',
                  'pending_orders']
        widgets = {
            'time': DateInput(),
        }


class AdminReturnsForm(forms.ModelForm):
    class Meta:
        model = AdminReturns
        fields = ['time', 'assigned_day', 'no_of_return', 'no_of_lines', 'total_quantities']
        widgets = {
            'time': DateInput(),
        }


class AdminCapacityForm(forms.ModelForm):
    class Meta:
        model = AdminCapacity
        fields = ['time', 'assigned_day', 'total_available_locations_and_accupied']
        widgets = {
            'time': DateInput(),
        }


class AdminInventoryForm(forms.ModelForm):
    class Meta:
        model = AdminInventory
        fields = ['time', 'assigned_day', 'last_movement']
        widgets = {
            'time': DateInput(),
        }
