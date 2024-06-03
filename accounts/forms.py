from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_admin = forms.BooleanField(required=False, label='Are you an admin?')
    is_company = forms.BooleanField(required=False, label='Are you a company?')

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'is_company')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_admin = self.cleaned_data['is_admin']
        user.is_company = self.cleaned_data['is_company']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'is_admin', 'is_company']
