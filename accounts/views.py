from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from .forms import CustomUserCreationForm, ProfileForm, AdminDataForm, \
    CustomerOutboundForm, \
    CustomerInboundForm, CustomerForm, CustomerReturnsForm, CustomerExpiryForm, CustomerDamageForm, \
    CustomerTravelDistanceForm, CustomerInventoryForm, CustomerPalletLocationAvailabilityForm, CustomerHSEForm, \
    AdminInboundForm, AdminOutboundForm, AdminReturnsForm, AdminCapacityForm, AdminInventoryForm
from .models import CustomUser

User = get_user_model()


# Create your views here.

class CustomLoginView(AuthLoginView):
    template_name = 'accounts/new/login.html'


class CustomLoginView(AuthLoginView):
    template_name = 'accounts/new/login.html'

    def form_valid(self, form):
        user = form.get_user()
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
    success_url = reverse_lazy('dashboard')  # Placeholder, will be overridden in form_valid

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        if user.is_admin:
            return redirect('/admin_dashboard/')
        elif user.is_customer:
            return redirect('/customer_dashboard/')
        elif user.is_employee:
            return redirect('/employee_dashboard/')
        else:
            return redirect('/')  # If needed


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
                elif user.is_admin:
                    if user.is_approved:
                        return redirect('/accounts/admin_dashboard/')
                    else:
                        logout(request)
                        return HttpResponse("Your admin account is awaiting approval.")
                elif user.is_customer:
                    return redirect('/customer/customer_dashboard/')
                elif user.is_employee:
                    return redirect('/accounts/employee_dashboard/')
                else:
                    return redirect('/')
        return render(request, self.template_name, {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'


@login_required
@staff_member_required
def approve_users_view(request):
    users_to_approve = User.objects.filter(is_admin=True, is_approved=False)
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
    if request.method == 'POST':
        admin_data_form = AdminDataForm(request.POST)
        customer_form = CustomerForm(request.POST)
        customer_inbound_form = CustomerInboundForm(request.POST)
        customer_outbound_form = CustomerOutboundForm(request.POST)

        if admin_data_form.is_valid():
            admin_data_form.save()
            return redirect('some_success_url')
        elif customer_form.is_valid() and customer_inbound_form.is_valid() and customer_outbound_form.is_valid():
            customer_form.save()
            customer_inbound_form.save()
            customer_outbound_form.save()
            return redirect('some_success_url')
    else:
        admin_data_form = AdminDataForm()
        customer_form = CustomerForm()
        customer_inbound_form = CustomerInboundForm()
        customer_outbound_form = CustomerOutboundForm()

    context = {
        'admin_data_form': admin_data_form,
        'customer_form': customer_form,
        'customer_inbound_form': customer_inbound_form,
        'customer_outbound_form': customer_outbound_form,
    }

    return render(request, 'general/dashboard/default/components/employee_dashboard.html')


@login_required
@user_passes_test(is_employee)
def add_admin_data(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        inbound_form = CustomerInboundForm(request.POST)
        outbound_form = CustomerOutboundForm(request.POST)
        returns_form = CustomerReturnsForm(request.POST)
        expiry_form = CustomerExpiryForm(request.POST)
        damage_form = CustomerDamageForm(request.POST)
        travel_distance_form = CustomerTravelDistanceForm(request.POST)
        inventory_form = CustomerInventoryForm(request.POST)
        pallet_location_availability_form = CustomerPalletLocationAvailabilityForm(request.POST)
        hse_form = CustomerHSEForm(request.POST)
        admin_data_form = AdminDataForm(request.POST)
        admin_inbound_form = AdminInboundForm(request.POST)
        admin_outbound_form = AdminOutboundForm(request.POST)
        admin_returns_form = AdminReturnsForm(request.POST)
        admin_capacity_form = AdminCapacityForm(request.POST)
        admin_inventory_form = AdminInventoryForm(request.POST)

        if all([customer_form.is_valid(), inbound_form.is_valid(), outbound_form.is_valid(), returns_form.is_valid(),
                expiry_form.is_valid(), damage_form.is_valid(), travel_distance_form.is_valid(),
                inventory_form.is_valid(), pallet_location_availability_form.is_valid(), hse_form.is_valid(),
                admin_data_form.is_valid(), admin_inbound_form.is_valid(), admin_outbound_form.is_valid(),
                admin_returns_form.is_valid(), admin_capacity_form.is_valid(), admin_inventory_form.is_valid()]):
            customer_form.save()
            inbound_form.save()
            outbound_form.save()
            returns_form.save()
            expiry_form.save()
            damage_form.save()
            travel_distance_form.save()
            inventory_form.save()
            pallet_location_availability_form.save()
            hse_form.save()
            admin_data_form.save()
            admin_inbound_form.save()
            admin_outbound_form.save()
            admin_returns_form.save()
            admin_capacity_form.save()
            admin_inventory_form.save()
            return redirect('success')

    else:
        customer_form = CustomerForm()
        inbound_form = CustomerInboundForm()
        outbound_form = CustomerOutboundForm()
        returns_form = CustomerReturnsForm()
        expiry_form = CustomerExpiryForm()
        damage_form = CustomerDamageForm()
        travel_distance_form = CustomerTravelDistanceForm()
        inventory_form = CustomerInventoryForm()
        pallet_location_availability_form = CustomerPalletLocationAvailabilityForm()
        hse_form = CustomerHSEForm()
        admin_data_form = AdminDataForm()
        admin_inbound_form = AdminInboundForm()
        admin_outbound_form = AdminOutboundForm()
        admin_returns_form = AdminReturnsForm()
        admin_capacity_form = AdminCapacityForm()
        admin_inventory_form = AdminInventoryForm()

    context = {
        'customer_form': customer_form,
        'inbound_form': inbound_form,
        'outbound_form': outbound_form,
        'returns_form': returns_form,
        'expiry_form': expiry_form,
        'damage_form': damage_form,
        'travel_distance_form': travel_distance_form,
        'inventory_form': inventory_form,
        'pallet_location_availability_form': pallet_location_availability_form,
        'hse_form': hse_form,
        'admin_data_form': admin_data_form,
        'admin_inbound_form': admin_inbound_form,
        'admin_outbound_form': admin_outbound_form,
        'admin_returns_form': admin_returns_form,
        'admin_capacity_form': admin_capacity_form,
        'admin_inventory_form': admin_inventory_form,
    }
    return render(request, 'general/dashboard/default/components/add_admin_data.html', context)
