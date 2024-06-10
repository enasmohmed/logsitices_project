# forms.py
from django import forms

from .models import Company, Inbound


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class InboundForm(forms.ModelForm):
    class Meta:
        model = Inbound
        fields = '__all__'

# قم بإنشاء نماذج مماثلة لبقية النماذج الخاصة بك
