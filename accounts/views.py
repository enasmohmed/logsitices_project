from django.contrib.auth import login, authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as AuthLoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView

from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser


# Create your views here.

class CustomLoginView(AuthLoginView):
    template_name = 'accounts/new/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if user.is_superuser:
            return redirect('admin_dashboard')
        elif user.is_company:
            return redirect(reverse('customer_dashboard'))
        else:
            return redirect('/')


class CustomRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/new/sign-up.html'
    success_url = reverse_lazy('dashboard')  # Placeholder, will be overridden in form_valid

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        if user.is_admin:
            return redirect('admin_dashboard')
        elif user.is_company:
            return redirect('company_dashboard')
        else:
            return redirect('default_dashboard')  # If needed


class RegisterView(View):
    form_class = CustomUserCreationForm
    template_name = 'accounts/new/sign-up.html'

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
def company_dashboard(request):
    return render(request, 'accounts/company_dashboard.html')


class CustomLogoutView(auth_views.LogoutView):
    next_page = 'accounts/new/login/'


def profile_view(request):
    user = request.user
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    return render(request, 'profile.html', {'form': form})


# ---------------------------------user
@login_required(login_url="/login")
def user_profile(request):
    # الحصول على بيانات فتات الخبز
    context = {
        "breadcrumb": {
            "title": "User Profile",
            "parent": "Users",
            "child": "User Profile"
        }
    }

    # الحصول على المستخدم الحالي
    user = request.user

    # إنشاء نموذج مملوء ببيانات المستخدم الحالي
    form = ProfileForm(instance=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    # تمرير النموذج إلى القالب
    context['form'] = form

    # تحديد ما إذا كان المستخدم مسجل كمسؤول أو كشركة
    is_admin = user.is_admin
    is_company = user.is_company

    # إضافة المتغيرات إلى السياق
    context['is_admin'] = is_admin
    context['is_company'] = is_company

    context['date_joined'] = user.date_joined
    context['last_login'] = user.last_login

    return render(request, "accounts/user/user-profile/user-profile.html", context)


@login_required(login_url="/login")
def edit_profile(request):
    context = {"breadcrumb": {"title": "Edit Profile", "parent": "Users", "child": "Edit Profile"}}
    return render(request, "accounts/user/edit-profile/edit-profile.html", context)


@login_required(login_url="/login")
def user_cards(request):
    context = {"breadcrumb": {"title": "User Cards", "parent": "Users", "child": "User Cards"}}
    return render(request, "accounts/user/user-cards/user-cards.html", context)
