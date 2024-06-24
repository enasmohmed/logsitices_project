from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView

from .forms import CustomUserCreationForm, ProfileForm, AdminDataForm, CustomerForm
from .models import CustomUser

User = get_user_model()


# Create your views here.


class CustomLoginView(AuthLoginView):
    template_name = 'accounts/new/login.html'

    def form_valid(self, form):
        user = form.get_user()
        password = form.cleaned_data.get('password')

        # Check if the user is superuser
        if user.is_superuser:
            login(self.request, user)
            return redirect('/accounts/admin_dashboard/')

        # For non-superuser accounts
        if not user.is_approved:
            logout(self.request)
            messages.error(self.request, "Your account is pending approval.")
            return redirect('/accounts/login/')

        login(self.request, user)
        if user.is_admin:
            return redirect('/accounts/admin_dashboard/')
        elif user.is_customer:
            return redirect('/accounts/customer_dashboard/')
        elif user.is_employee:
            return redirect('/accounts/employee_dashboard/')
        else:
            return redirect('/')


class CustomRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/new/sign-up.html'
    success_url = reverse_lazy('login')  # Redirect to login page

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request,
                         "Your account has been created successfully. Your account is now pending approval.")
        return redirect('login')


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
            return HttpResponse("Your account is awaiting approval.")
        return render(request, self.template_name, {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'


@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_users_view(request):
    users_to_approve = User.objects.filter(is_approved=False)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.is_approved = True
        user.save()
        return redirect('approve_users')

    return render(request, 'accounts/approve_users.html', {'users': users_to_approve})


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
    is_customer = user.is_customer
    is_employee = user.is_employee

    # إضافة المتغيرات إلى السياق
    context['is_admin'] = is_admin
    context['is_customer'] = is_customer
    context['is_employee'] = is_employee

    context['date_joined'] = user.date_joined
    context['last_login'] = user.last_login

    return render(request, "user/user-profile/user-profile.html", context)


@login_required(login_url="/login")
def edit_profile(request):
    context = {"breadcrumb": {"title": "Edit Profile", "parent": "Users", "child": "Edit Profile"}}
    return render(request, "accounts/user/edit-profile/edit-profile.html", context)


@login_required(login_url="/login")
def user_cards(request):
    context = {"breadcrumb": {"title": "User Cards", "parent": "Users", "child": "User Cards"}}
    return render(request, "accounts/user/user-cards/user-cards.html", context)


def is_employee(user):
    return user.is_authenticated and user.is_employee


@login_required
@user_passes_test(is_employee)
def employee_dashboard(request):
    return render(request, 'general/dashboard/default/components/employee_dashboard.html')


def is_employee(user):
    return user.is_employee


@method_decorator([login_required, user_passes_test(is_employee)], name='dispatch')
class AddAdminDataView(View):
    def get(self, request):
        context = {
            'admin_data_form': AdminDataForm(),
            'customer_form': CustomerForm(),
        }
        return render(request, 'general/dashboard/default/components/add_admin_data.html', context)

    def post(self, request):
        data_type = request.POST.get('data_type')
        if data_type == 'admin':
            form = AdminDataForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Admin data added successfully.')
                return redirect('accounts:employee_dashboard')
            else:
                messages.error(request, 'Invalid admin data. Please check the form.')
                return redirect('add_admin_data')  # Redirect back to the same page
        elif data_type == 'customer':
            form = CustomerForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Customer data added successfully.')
                return redirect('accounts:customer_dashboard')
            else:
                messages.error(request, 'Invalid customer data. Please check the form.')
                return redirect('add_admin_data')  # Redirect back to the same page

        # If no data type is selected or other error occurred, redirect back to the same page
        return redirect('add_admin_data')
