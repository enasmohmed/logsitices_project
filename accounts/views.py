from django.contrib.auth import login, authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as AuthLoginView
from django.shortcuts import render, redirect
from django.views import View

from .forms import CustomUserCreationForm


# Create your views here.

class CustomLoginView(AuthLoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if user.is_superuser:
            return redirect('admin_dashboard')
        elif user.is_company:
            return redirect('company_dashboard')
        else:
            return redirect('/')


class RegisterView(View):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('/accounts/admin_dashboard/')
                elif user.is_company:
                    return redirect('/accounts/company_dashboard/')
                else:
                    return redirect('home')
        return render(request, self.template_name, {'form': form})


@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')


@login_required
def company_dashboard(request):
    return render(request, 'accounts/company_dashboard.html')


class CustomLogoutView(auth_views.LogoutView):
    next_page = '/accounts/login/'
