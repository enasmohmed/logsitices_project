import calendar

from django.contrib import messages
from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, TemplateView

from administration.forms import AdminDataForm
from administration.models import AdminData
from customer.forms import CustomerForm
from customer.models import CustomerInbound, CustomerOutbound, CustomerReturns, CustomerExpiry, CustomerDamage, \
    CustomerTravelDistance, CustomerInventory, CustomerPalletLocationAvailability, CustomerHSE
from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser

User = get_user_model()


# Create your views here.


class CustomLoginView(AuthLoginView):
    template_name = 'accounts/new/login.html'

    def form_valid(self, form):
        user = form.get_user()
        print(f"User: {user.username}, Approved: {user.is_approved}")

        # Print detailed role information
        if hasattr(user, 'role'):
            print(f"Role attribute exists. Role: {user.role}")
        else:
            print("Role attribute does not exist.")

        # Print group memberships
        print(f"Groups: {[group.name for group in user.groups.all()]}")

        if not user.is_superuser and not user.is_approved:
            messages.error(self.request, "Your account is pending approval.")
            logout(self.request)
            return redirect('accounts:login')

        login(self.request, user)

        if user.is_superuser or user.groups.filter(name='Admin').exists():
            print("Redirecting to admin dashboard")
            return redirect(reverse('accounts:admin_dashboard'))
        elif user.role == 'customer' and user.groups.filter(name='Customer').exists():
            print("Redirecting to customer dashboard")
            return redirect('accounts:customer_dashboard')
        elif user.role == 'employee' and user.groups.filter(name='Employee').exists():
            print("Redirecting to employee dashboard")
            return redirect('accounts:choose_dashboard')
        else:
            print("Redirecting to home page")
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
        return redirect(self.success_url)


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


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ApproveUsersView(TemplateView):
    template_name = 'accounts/approve_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.filter(is_approved=False)
        context['breadcrumb'] = {
            "title": "Approve Users",
            "parent": "Super User",
            "child": "Admin"
        }
        return context

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        user.is_approved = True

        # إذا كان المستخدم سوبر يوزر، الموافقة عليه وإعادته كـ staff
        if user.is_superuser:
            user.is_staff = True
            user.save()
            messages.success(request, f'تمت الموافقة على المستخدم {user.username} وهو سوبر يوزر.')
        else:
            user.is_staff = True  # تعيين المستخدم كـstaff
            user.save()

            # إضافة المستخدم إلى الجروب المناسب بناءً على دوره
            if user.user_type == 'admin':
                group, created = Group.objects.get_or_create(name='Admin')
            elif user.user_type == 'customer':
                group, created = Group.objects.get_or_create(name='Customer')
            elif user.user_type == 'employee':
                group, created = Group.objects.get_or_create(name='Employee')

            user.groups.add(group)
            user.save()
            messages.success(request,
                             f'تمت الموافقة على المستخدم {user.username} وتم إضافته إلى المجموعة {group.name}.')

        return redirect('accounts:approve_users')


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
    context = {
        "breadcrumb": {
            "title": "User Profile",
            "parent": "Users",
            "child": "User Profile"
        }
    }

    user = request.user
    form = ProfileForm(instance=user)

    # تحديد نوع المستخدم بناءً على الصلاحيات وعضوية المجموعة
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        user_type = "Admin"
    elif user.groups.filter(name='Employee').exists():
        user_type = "Employee"
    else:
        user_type = "Customer"

    # الحصول على أسماء المجموعات التي ينتمي إليها المستخدم
    user_groups = user.groups.values_list('name', flat=True)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    context['form'] = form
    context['user_type'] = user_type
    context['user_groups'] = user_groups

    return render(request, "user/user-profile/user-profile.html", context)


@login_required(login_url="/login")
def redirect_to_dashboard(request):
    user = request.user
    if request.method == 'POST':
        dashboard_choice = request.POST.get('dashboard_choice')

        request.session['dashboard_choice'] = dashboard_choice
        if user.role == 'employee':
            if dashboard_choice == 'admin_dashboard':
                return redirect('accounts:admin_dashboard')
        elif dashboard_choice == 'customer_dashboard':
            return redirect('accounts:customer_dashboard')

    # التحقق من إذا كان المستخدم مشرفًا فائق الصلاحيات أو له دور 'admin'
    if user.is_superuser or user.role == 'admin':
        return redirect('accounts:admin_dashboard')

    # التحقق من إذا كان للمستخدم دور 'employee'
    elif user.role == 'employee':
        return redirect('accounts:admin_dashboard')

    # إذا لم يكن المستخدم مشرفًا أو موظفًا، افتراض أن المستخدم له دور 'customer'
    elif user.role == 'customer':
        return redirect('accounts:customer_dashboard')

    # يمكنك إضافة إعادة توجيه افتراضية هنا إذا كان نوع المستخدم غير معروف
    return redirect('accounts:default_dashboard')


@user_passes_test(lambda u: u.is_superuser)
def user_cards(request):
    # التحقق إذا كان المستخدم الحالي هو سوبر يوزر
    if not request.user.is_superuser:
        return redirect('/')

    # جلب جميع المستخدمين
    users = CustomUser.objects.all()

    # تحديد نوع المستخدم بناءً على الصلاحيات وعضوية المجموعة
    if request.user.is_superuser:
        user_type = "Admin"
    elif request.user.groups.filter(name='Employee').exists():
        user_type = "Employee"
    else:
        user_type = "Customer"

    # تحديد مجموعة المستخدم
    user_group = "Unknown"  # افتراض قيمة افتراضية

    if request.user.is_superuser:
        user_group = "Admin"
    elif request.user.groups.filter(name='Employee').exists():
        user_group = "Employee"
    elif request.user.groups.filter(name='Customer').exists():
        user_group = "Customer"

    context = {
        "breadcrumb": {
            "title": "User Cards",
            "parent": "Users",
            "child": "User Cards"
        },
        "users": users,
        "user_type": user_type,  # إضافة user_type إلى السياق
        "user_group": user_group,  # إضافة user_group إلى السياق
    }

    return render(request, "user/user-cards/user-cards.html", context)


def is_employee(user):
    return user.is_authenticated and user.role == 'employee'


@method_decorator([login_required, user_passes_test(is_employee)], name='dispatch')
class EmployeeDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = {
            "title": "Employee Dashboard",
            "parent": "Dashboard",
            "child": "Employee"
        }

        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        day = self.request.GET.get('day')

        # فلترة البيانات بناءً على القيم المدخلة
        inbound_data = CustomerInbound.objects.all()
        outbound_data = CustomerOutbound.objects.all()
        returns_data = CustomerReturns.objects.all()
        expiry_data = CustomerExpiry.objects.all()
        damage_data = CustomerDamage.objects.all()
        travel_distance_data = CustomerTravelDistance.objects.all()
        inventory_data = CustomerInventory.objects.all()
        pallet_location_availability_data = CustomerPalletLocationAvailability.objects.all()
        hse_data = CustomerHSE.objects.all()

        if year:
            inbound_data = inbound_data.filter(time__year=year)
            outbound_data = outbound_data.filter(time__year=year)
            returns_data = returns_data.filter(time__year=year)
            expiry_data = expiry_data.filter(time__year=year)
            damage_data = damage_data.filter(time__year=year)
            travel_distance_data = travel_distance_data.filter(time__year=year)
            inventory_data = inventory_data.filter(time__year=year)
            pallet_location_availability_data = pallet_location_availability_data.filter(time__year=year)
            hse_data = hse_data.filter(time__year=year)

        if month:
            inbound_data = inbound_data.filter(time__month=month)
            outbound_data = outbound_data.filter(time__month=month)
            returns_data = returns_data.filter(time__month=month)
            expiry_data = expiry_data.filter(time__month=month)
            damage_data = damage_data.filter(time__month=month)
            travel_distance_data = travel_distance_data.filter(time__month=month)
            inventory_data = inventory_data.filter(time__month=month)
            pallet_location_availability_data = pallet_location_availability_data.filter(time__month=month)
            hse_data = hse_data.filter(time__month=month)

        if day:
            inbound_data = inbound_data.filter(time__day=day)
            outbound_data = outbound_data.filter(time__day=day)
            returns_data = returns_data.filter(time__day=day)
            expiry_data = expiry_data.filter(time__day=day)
            damage_data = damage_data.filter(time__day=day)
            travel_distance_data = travel_distance_data.filter(time__day=day)
            inventory_data = inventory_data.filter(time__day=day)
            pallet_location_availability_data = pallet_location_availability_data.filter(time__day=day)
            hse_data = hse_data.filter(time__day=day)

        # إضافة البيانات المفلترة إلى السياق
        context['inbound_data'] = inbound_data
        context['outbound_data'] = outbound_data
        context['returns_data'] = returns_data
        context['expiry_data'] = expiry_data
        context['damage_data'] = damage_data
        context['travel_distance_data'] = travel_distance_data
        context['inventory_data'] = inventory_data
        context['pallet_location_availability_data'] = pallet_location_availability_data
        context['hse_data'] = hse_data

        # الحصول على جميع بيانات Inbound
        context['inbound_data'] = inbound_data
        context['total_shipments_in_asn'] = inbound_data.aggregate(Sum('total_shipments_in_asn'))[
                                                'total_shipments_in_asn__sum'] or 0
        context['total_arrived'] = inbound_data.aggregate(Sum('arrived'))['arrived__sum'] or 0
        context['total_no_show'] = inbound_data.aggregate(Sum('no_show'))['no_show__sum'] or 0

        context['total_waiting_for_inspection'] = inbound_data.aggregate(Sum('waiting_for_inspection'))[
                                                      'waiting_for_inspection__sum'] or 0
        context['total_dash_of_GR_reports_shared'] = \
            inbound_data.aggregate(Sum('total_dash_of_GR_reports_shared'))['total_dash_of_GR_reports_shared__sum'] or 0
        context['total_dash_of_GR_reports_with_discripancy'] = \
            inbound_data.aggregate(Sum('dash_of_GR_reports_with_discripancy'))[
                'dash_of_GR_reports_with_discripancy__sum'] or 0

        context['total_received_completely'] = inbound_data.aggregate(Sum('received_completely'))[
                                                   'received_completely__sum'] or 0
        context['total_received_partially'] = inbound_data.aggregate(Sum('received_partially'))[
                                                  'received_partially__sum'] or 0
        context['total_rejected_completely'] = inbound_data.aggregate(Sum('rejected_completely'))[
                                                   'rejected_completely__sum'] or 0

        # الحصول على جميع بيانات Outound
        context['outbound_data'] = outbound_data
        context['total_order_received_from_npco'] = outbound_data.aggregate(Sum('order_received_from_npco'))[
                                                        'order_received_from_npco__sum'] or 0
        context['total_pending_orders'] = outbound_data.aggregate(Sum('pending_orders'))['pending_orders__sum'] or 0
        context['total_number_of_orders_that_are_delivered_today'] = \
            outbound_data.aggregate(Sum('number_of_orders_that_are_delivered_today'))[
                'number_of_orders_that_are_delivered_today__sum'] or 0

        context['total_number_of_PODs_collected_on_time'] = \
            outbound_data.aggregate(Sum('number_of_PODs_collected_on_time'))[
                'number_of_PODs_collected_on_time__sum'] or 0
        context['total_number_of_PODs_collected_Late'] = outbound_data.aggregate(Sum('number_of_PODs_collected_Late'))[
                                                             'number_of_PODs_collected_Late__sum'] or 0
        context['total_total_skus_picked'] = outbound_data.aggregate(Sum('total_skus_picked'))[
                                                 'total_skus_picked__sum'] or 0

        # الحصول على جميع بيانات Returns
        context['returns_data'] = returns_data
        context['total_orders_items_returned'] = returns_data.aggregate(Sum('total_orders_items_returned'))[
                                                     'total_orders_items_returned__sum'] or 0
        context['total_number_of_return_items_orders_updated_on_time'] = \
            returns_data.aggregate(Sum('number_of_return_items_orders_updated_on_time'))[
                'number_of_return_items_orders_updated_on_time__sum'] or 0
        context['total_number_of_return_items_orders_updated_late'] = \
            returns_data.aggregate(Sum('number_of_return_items_orders_updated_late'))[
                'number_of_return_items_orders_updated_late__sum'] or 0

        # الحصول على جميع بيانات Expiry
        context['expiry_data'] = expiry_data
        context['total_SKUs_expired'] = expiry_data.aggregate(Sum('total_SKUs_expired'))['total_SKUs_expired__sum'] or 0
        context['total_expired_SKUS_disposed'] = expiry_data.aggregate(Sum('total_expired_SKUS_disposed'))[
                                                     'total_expired_SKUS_disposed__sum'] or 0
        context['total_nearly_expired_1_to_3_months'] = expiry_data.aggregate(Sum('nearly_expired_1_to_3_months'))[
                                                            'nearly_expired_1_to_3_months__sum'] or 0
        context['total_nearly_expired_3_to_6_months'] = expiry_data.aggregate(Sum('nearly_expired_3_to_6_months'))[
                                                            'nearly_expired_3_to_6_months__sum'] or 0

        # Damage
        context['damage_data'] = damage_data
        context['Total_QTYs_Damaged_by_WH'] = damage_data.aggregate(Sum('Total_QTYs_Damaged_by_WH'))[
                                                  'Total_QTYs_Damaged_by_WH__sum'] or 0
        context['Total_Number_of_Damaged_during_receiving'] = \
            damage_data.aggregate(Sum('Number_of_Damaged_during_receiving'))[
                'Number_of_Damaged_during_receiving__sum'] or 0
        context['Total_Damaged_QTYs_Disposed'] = damage_data.aggregate(Sum('Total_Damaged_QTYs_Disposed'))[
                                                     'Total_Damaged_QTYs_Disposed__sum'] or 0

        # الحصول على جميع بيانات TravelDistance
        context['travel_distance_data'] = travel_distance_data
        context['Total_no_of_Pallet_deliverd'] = travel_distance_data.aggregate(Sum('Total_no_of_Pallet_deliverd'))[
                                                     'Total_no_of_Pallet_deliverd__sum'] or 0
        context['Total_no_of_Customers_deliverd'] = \
            travel_distance_data.aggregate(Sum('Total_no_of_Customers_deliverd'))[
                'Total_no_of_Customers_deliverd__sum'] or 0

        # Inventory
        context['inventory_data'] = inventory_data
        context['Total_Locations_Audited'] = inventory_data.aggregate(Sum('Total_Locations_Audited'))[
                                                 'Total_Locations_Audited__sum'] or 0
        context['Total_Locations_with_Incorrect_SKU_and_Qty'] = \
            inventory_data.aggregate(Sum('Total_Locations_with_Incorrect_SKU_and_Qty'))[
                'Total_Locations_with_Incorrect_SKU_and_Qty__sum'] or 0
        context['Total_SKUs_Reconciliation'] = inventory_data.aggregate(Sum('Total_SKUs_Reconciliation'))[
                                                   'Total_SKUs_Reconciliation__sum'] or 0

        # PalletLocationAvailability
        context['pallet_location_availability_data'] = pallet_location_availability_data
        context['Total_Storage_Pallet'] = pallet_location_availability_data.aggregate(Sum('Total_Storage_Pallet'))[
                                              'Total_Storage_Pallet__sum'] or 0
        context['Total_Storage_Bin'] = pallet_location_availability_data.aggregate(Sum('Total_Storage_Bin'))[
                                           'Total_Storage_Bin__sum'] or 0
        context['Total_Storage_pallet_empty'] = \
            pallet_location_availability_data.aggregate(Sum('Total_Storage_pallet_empty'))[
                'Total_Storage_pallet_empty__sum'] or 0
        context['Total_Storage_Bin_empty'] = \
            pallet_location_availability_data.aggregate(Sum('Total_Storage_Bin_empty'))[
                'Total_Storage_Bin_empty__sum'] or 0
        context['Total_Storage_Bin_empty'] = \
            pallet_location_availability_data.aggregate(Sum('Total_Storage_Bin_empty'))[
                'Total_Storage_Bin_empty__sum'] or 0
        context['Total_occupied_pallet_location'] = \
            pallet_location_availability_data.aggregate(Sum('Total_occupied_pallet_location'))[
                'Total_occupied_pallet_location__sum'] or 0
        context['Total_occupied_Bin_location'] = \
            pallet_location_availability_data.aggregate(Sum('Total_occupied_Bin_location'))[
                'Total_occupied_Bin_location__sum'] or 0

        # HSE
        context['hse_data'] = hse_data
        context['Total_Incidents_on_the_side'] = hse_data.aggregate(Sum('Total_Incidents_on_the_side'))[
                                                     'Total_Incidents_on_the_side__sum'] or 0

        # Admin
        admin_data = AdminData.objects.all()
        context['admin_data'] = admin_data.all()
        context['total_no_of_employees'] = admin_data.aggregate(Sum('total_no_of_employees'))[
                                               'total_no_of_employees__sum'] or 0

        # الحصول على جميع السنين والشهور والأيام
        years = CustomerInbound.objects.dates('time', 'year')
        months = list(calendar.month_name)[1:]
        days = range(1, 32)  # للحصول على أيام الشهر

        context['current_user'] = self.request.user
        user_type = "Employee" if self.request.user.role == "employee" else "Customer"
        context['user_type'] = user_type

        context.update({
            'years': years,
            'months': months,
            'days': days,
        })
        return context


@method_decorator(login_required, name='dispatch')
class ChooseDashboardView(View):
    template_name = 'general/dashboard/default/components/choose_dashboard.html'

    def get_context_data(self, **kwargs):
        context = {
            "breadcrumb": {
                "title": "Employee Dashboard",
                "parent": "Edit Data",
                "child": "Default"
            }
        }

        # Determine user type and add it to the context
        if self.request.user.is_superuser:
            context['user_type'] = "Super Admin"
        elif self.request.user.groups.filter(name='Admin').exists():
            context['user_type'] = "Admin"
        elif self.request.user.groups.filter(name='Employee').exists():
            context['user_type'] = "Employee"
        else:
            context['user_type'] = "Unknown"

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({
            'admin_data_form': AdminDataForm(initial={'user': request.user}),
            'customer_form': CustomerForm(initial={'user': request.user}),
            'current_user': request.user.username  # Add current user's username to context
        })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        choice = request.POST.get('choice')
        if choice == 'admin_dashboard':
            if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
                return redirect('accounts:admin_dashboard')  # Replace with correct admin dashboard URL name
            elif request.user.groups.filter(name='Employee').exists():
                request.session['dashboard_choice'] = 'admin_dashboard'
                return redirect('accounts:admin_dashboard')  # Replace with correct admin dashboard URL name
        elif choice == 'customer_dashboard':
            request.session['dashboard_choice'] = 'customer_dashboard'
            return redirect('accounts:customer_dashboard')  # Replace with correct customer dashboard URL name

        # Get current user and their role
        current_user = request.user
        user_role = current_user.role  # Replace with correct way to fetch user role

        context = self.get_context_data(**kwargs)
        context.update({
            'admin_data_form': AdminDataForm(initial={'user': request.user}),
            'customer_form': CustomerForm(initial={'user': request.user}),
            'current_user': current_user.username,  # Add current user's username to context
            'user_role': user_role  # Add user role to context
        })
        return render(request, self.template_name, context)
