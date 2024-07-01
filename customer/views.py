import calendar
import json

import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from accounts.forms import CustomerForm, CustomerInboundForm, CustomerOutboundForm, CustomerReturnsForm, \
    CustomerExpiryForm, CustomerDamageForm, CustomerTravelDistanceForm, CustomerInventoryForm, \
    CustomerPalletLocationAvailabilityForm, CustomerHSEForm
from administration.models import AdminData
from .models import Customer, CustomerInbound, CustomerOutbound, CustomerReturns, CustomerExpiry, CustomerDamage, \
    CustomerTravelDistance, CustomerInventory, CustomerPalletLocationAvailability, CustomerHSE


### View Customer Dashboard
@method_decorator(login_required, name='dispatch')
class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check user's group membership
        user = self.request.user
        if user.is_authenticated:
            if user.groups.filter(name='Super Admin').exists() or user.groups.filter(name='Admin').exists():
                context['is_admin'] = True
            elif user.groups.filter(name='Employee').exists():
                context['is_employee'] = True
            elif user.groups.filter(name='Customer').exists():
                context['is_customer'] = True
            else:
                context['user_type'] = 'Unknown'
        else:
            context['user_type'] = 'Anonymous'

        context['breadcrumb'] = {
            "title": "Operation Dashboard",
            "parent": "Dashboard",
            "child": "Default"
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

        context['total_waiting_for_mod_inspection'] = inbound_data.aggregate(Sum('waiting_for_mod_inspection'))[
                                                          'waiting_for_mod_inspection__sum'] or 0
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

        if self.request.user.groups.filter(name='Customer'):
            context['user_type'] = "Customer"
        elif self.request.user.groups.filter(name='Employee').exists():
            context['user_type'] = "Employee"
        else:
            context['user_type'] = "Unknown"

        context.update({
            'years': years,
            'months': months,
            'days': days,
        })
        return context


### Edit Data Form Customer


### Edit Data Form Customer
class CustomerEditDataView(View):
    model_map = {
        'Customer': Customer,
        'CustomerInbound': CustomerInbound,
        'CustomerOutbound': CustomerOutbound,
        'CustomerReturns': CustomerReturns,
        'CustomerExpiry': CustomerExpiry,
        'CustomerDamage': CustomerDamage,
        'CustomerTravelDistance': CustomerTravelDistance,
        'CustomerInventory': CustomerInventory,
        'CustomerPalletLocationAvailability': CustomerPalletLocationAvailability,
        'CustomerHSE': CustomerHSE,
    }

    def is_employee_user(self, user):
        return user.groups.filter(name='Employee').exists()

    def is_customer_user(self, user):
        return user.groups.filter(name='Customer').exists()

    @method_decorator(login_required, name='dispatch')
    @method_decorator(csrf_exempt, name='dispatch')
    def get(self, request):
        user = request.user
        is_admin = user.is_staff
        is_employee = self.is_employee_user(user)
        is_customer = self.is_customer_user(user)

        dashboard_choice = request.session.get('dashboard_choice', 'customer_dashboard')

        if dashboard_choice not in ['admin_dashboard', 'customer_dashboard']:
            dashboard_choice = 'customer_dashboard'

        if dashboard_choice == 'admin_dashboard' and not is_admin:
            return HttpResponseForbidden("You do not have permission to access this page.")

        if dashboard_choice == 'customer_dashboard' and not (is_customer or is_employee):
            return HttpResponseForbidden("You do not have permission to access this page.")

        # تحديد دور المستخدم
        user_type = 'employee' if is_employee else 'customer'

        context = {
            "user": user,
            "is_admin": is_admin,
            "is_employee": is_employee,
            "is_customer": is_customer,
            "dashboard_choice": dashboard_choice,
            "user_type": user_type,  # إضافة دور المستخدم إلى السياق
            "breadcrumb": {
                "title": "Admin Dashboard" if dashboard_choice == 'admin_dashboard' else "Customer Dashboard",
                "parent": "Edit Data",
                "child": "Default"
            }
        }

        if dashboard_choice == 'admin_dashboard' and is_admin:
            admin_data = AdminData.objects.all()
            context["admin_data"] = admin_data
        elif dashboard_choice == 'customer_dashboard' or user.groups.filter(name='Customer').exists():
            companies = Customer.objects.all()
            inbounds = CustomerInbound.objects.all()
            outbounds = CustomerOutbound.objects.all()
            returns = CustomerReturns.objects.all()
            expiries = CustomerExpiry.objects.all()
            damages = CustomerDamage.objects.all()
            travel_distances = CustomerTravelDistance.objects.all()
            inventories = CustomerInventory.objects.all()
            pallet_location_availabilities = CustomerPalletLocationAvailability.objects.all()
            hses = CustomerHSE.objects.all()

            context.update({
                "companies": companies,
                "inbounds": inbounds,
                "outbounds": outbounds,
                "returns": returns,
                "expiries": expiries,
                "damages": damages,
                "travel_distances": travel_distances,
                "inventories": inventories,
                "pallet_location_availabilities": pallet_location_availabilities,
                "hses": hses,
            })

        return render(request, "excel.html", context)

    @method_decorator(login_required, name='dispatch')
    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        user = request.user
        is_admin = user.is_staff
        is_employee = self.is_employee_user(user)
        is_customer = self.is_customer_user(user)

        dashboard_choice = request.session.get('dashboard_choice', 'customer_dashboard')

        if dashboard_choice not in ['admin_dashboard', 'customer_dashboard']:
            dashboard_choice = 'customer_dashboard'

        if dashboard_choice == 'admin_dashboard' and not is_admin:
            return JsonResponse({"success": False, "error": "Permission denied."})

        if dashboard_choice == 'customer_dashboard' and not (is_customer or is_employee):
            return JsonResponse({"success": False, "error": "Permission denied."})

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"})

        if 'update' in data:
            model_name = data['update'].get('model')
            model_id = data['update'].get('id')
            field_name = data['update'].get('field')
            new_value = data['update'].get('value')

            if model_name in self.model_map:
                model = self.model_map[model_name]
                try:
                    obj = model.objects.get(id=model_id)
                except model.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Object not found"})

                setattr(obj, field_name, new_value)
                obj.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Invalid model"})
        elif 'add' in data:
            model_name = data['add'].get('model')
            fields = data['add'].get('fields', {})

            if model_name in self.model_map:
                model = self.model_map[model_name]
                obj = model(**fields)
                obj.save()
                return JsonResponse({"success": True, "id": obj.id})
            else:
                return JsonResponse({"success": False, "error": "Invalid model"})
        elif 'delete' in data:
            model_name = data['delete'].get('model')
            model_id = data['delete'].get('id')

            if model_name in self.model_map:
                model = self.model_map[model_name]
                try:
                    obj = model.objects.get(id=model_id)
                except model.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Object not found"})

                obj.delete()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Invalid model"})

        return JsonResponse({"success": False, "error": "Invalid operation"})


### Add Data Form Customer
def is_employee(user):
    return user.groups.filter(name='Employee').exists()


@method_decorator([login_required, user_passes_test(is_employee)], name='dispatch')
class AddCustomerDataView(View):
    def get(self, request):
        current_user = request.user.username  # Get current user's username
        user_type = ''

        if request.user.groups.filter(name='Super Admin').exists():
            user_type = 'Super Admin'
        elif request.user.groups.filter(name='Admin').exists():
            user_type = 'Admin'
        elif request.user.groups.filter(name='Employee').exists():
            user_type = 'Employee'
        elif request.user.groups.filter(name='Customer').exists():
            user_type = 'Customer'
        else:
            user_type = 'Unknown'

        context = {
            'customer_form': CustomerForm(initial={'user': request.user}),
            'customer_inbound_form': CustomerInboundForm(),
            'customer_outbound_form': CustomerOutboundForm(),
            'customer_returns_form': CustomerReturnsForm(),
            'customer_expiry_form': CustomerExpiryForm(),
            'customer_damage_form': CustomerDamageForm(),
            'customer_travel_distance_form': CustomerTravelDistanceForm(),
            'customer_inventory_form': CustomerInventoryForm(),
            'customer_pallet_location_availability_form': CustomerPalletLocationAvailabilityForm(),
            'customer_hse_form': CustomerHSEForm(),
            'current_user': current_user,  # Add current user's username to context
            'user_type': user_type,  # Add user type to context
            'breadcrumb': {
                'title': 'Employee Dashboard',
                'parent': 'Edit Data',
                'child': 'Default'
            }
        }
        return render(request, 'general/dashboard/default/components/add_admin_data.html', context)

    def post(self, request):
        customer_form = CustomerForm(request.POST)
        customer_inbound_form = CustomerInboundForm(request.POST)
        customer_outbound_form = CustomerOutboundForm(request.POST)
        customer_returns_form = CustomerReturnsForm(request.POST)
        customer_expiry_form = CustomerExpiryForm(request.POST)
        customer_damage_form = CustomerDamageForm(request.POST)
        customer_travel_distance_form = CustomerTravelDistanceForm(request.POST)
        customer_inventory_form = CustomerInventoryForm(request.POST)
        customer_pallet_location_availability_form = CustomerPalletLocationAvailabilityForm(request.POST)
        customer_hse_form = CustomerHSEForm(request.POST)

        forms = [
            customer_form,
            customer_inbound_form,
            customer_outbound_form,
            customer_returns_form,
            customer_expiry_form,
            customer_damage_form,
            customer_travel_distance_form,
            customer_inventory_form,
            customer_pallet_location_availability_form,
            customer_hse_form
        ]

        if all(form.is_valid() for form in forms):
            try:
                with transaction.atomic():
                    customer_data = customer_form.save(commit=False)
                    customer_data.user = request.user  # Assign the current user
                    customer_data.save()

                    customer_inbound_form.instance.customer = customer_data
                    customer_outbound_form.instance.customer = customer_data
                    customer_returns_form.instance.customer = customer_data
                    customer_expiry_form.instance.customer = customer_data
                    customer_damage_form.instance.customer = customer_data
                    customer_travel_distance_form.instance.customer = customer_data
                    customer_inventory_form.instance.customer = customer_data
                    customer_pallet_location_availability_form.instance.customer = customer_data
                    customer_hse_form.instance.customer = customer_data

                    customer_inbound_form.save()
                    customer_outbound_form.save()
                    customer_returns_form.save()
                    customer_expiry_form.save()
                    customer_damage_form.save()
                    customer_travel_distance_form.save()
                    customer_inventory_form.save()
                    customer_pallet_location_availability_form.save()
                    customer_hse_form.save()

                messages.success(request, 'Customer data added successfully.')
                return redirect('accounts:customer_dashboard')

            except Exception as e:
                messages.error(request, f'Failed to save customer data. Error: {str(e)}')
                return redirect('accounts:add_customer_data')

        else:
            for form in forms:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)

            return redirect('accounts:add_customer_data')


def export_to_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="data.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Data')

    row_num = 0
    columns = ['ID', 'Name', 'User']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num])

    rows = Customer.objects.all().values_list('id', 'name_company', 'user__username')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num])

    wb.save(response)
    return response


def export_to_pdf(request):
    # احصل على بيانات الجداول من طلب الويب
    data = request.POST.get('data')

    # تحويل البيانات إلى ملف PDF وحفظها

    # إرجاع رابط لتحميل الملف
    return JsonResponse({'download_url': ' excel.html'})
