# forms.py
from django import forms

from customer.models import CustomerInbound, Customer, CustomerOutbound, CustomerReturns, CustomerExpiry, \
    CustomerDamage, CustomerTravelDistance, CustomerPalletLocationAvailability, CustomerHSE


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class InboundForm(forms.ModelForm):
    class Meta:
        model = CustomerInbound
        fields = '__all__'


class OutboundForm(forms.ModelForm):
    class Meta:
        model = CustomerOutbound
        fields = '__all__'


class ReturnsForm(forms.ModelForm):
    class Meta:
        model = CustomerReturns
        fields = '__all__'


class ExpiryForm(forms.ModelForm):
    class Meta:
        model = CustomerExpiry
        fields = '__all__'


class DamageForm(forms.ModelForm):
    class Meta:
        model = CustomerDamage
        fields = '__all__'


class TravelDistanceForm(forms.ModelForm):
    class Meta:
        model = CustomerTravelDistance
        fields = '__all__'


class PalletLocationAvailabilityForm(forms.ModelForm):
    class Meta:
        model = CustomerPalletLocationAvailability
        fields = '__all__'


class HSEForm(forms.ModelForm):
    class Meta:
        model = CustomerHSE
        fields = '__all__'
