import calendar
import json
from io import BytesIO

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph

from administration.models import AdminData
from .forms import CustomerInboundForm, CustomerForm, CustomerReturnsForm, CustomerExpiryForm, \
    CustomerDamageForm, CustomerInventoryForm, CustomerPalletLocationAvailabilityForm, \
    CustomerHSEForm, CustomerTransportationOutboundForm, CustomerWHOutboundForm
from .models import Customer, CustomerInbound, CustomerTransportationOutbound,CustomerWHOutbound, CustomerReturns, CustomerExpiry, CustomerDamage, \
     CustomerInventory, CustomerPalletLocationAvailability, CustomerHSE, EmployeeProfile

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
            "title": "Healthcare Dashboard",
            "parent": "Dashboard",
            "child": "Default"
        }

        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        day = self.request.GET.get('day')

        # فلترة البيانات بناءً على القيم المدخلة
        inbound_data = CustomerInbound.objects.all()
        transportation_outbound_data = CustomerTransportationOutbound.objects.all()
        wh_outbound_data = CustomerWHOutbound.objects.all()
        returns_data = CustomerReturns.objects.all()
        expiry_data = CustomerExpiry.objects.all()
        damage_data = CustomerDamage.objects.all()
        inventory_data = CustomerInventory.objects.all()
        pallet_location_availability_data = CustomerPalletLocationAvailability.objects.all()
        hse_data = CustomerHSE.objects.all()

        if year:
            inbound_data = inbound_data.filter(time__year=year)
            transportation_outbound_data = transportation_outbound_data.filter(time__year=year)
            wh_outbound_data = wh_outbound_data.filter(time__year=year)
            returns_data = returns_data.filter(time__year=year)
            expiry_data = expiry_data.filter(time__year=year)
            damage_data = damage_data.filter(time__year=year)
            inventory_data = inventory_data.filter(time__year=year)
            pallet_location_availability_data = pallet_location_availability_data.filter(time__year=year)
            hse_data = hse_data.filter(time__year=year)

        if month:
            inbound_data = inbound_data.filter(time__month=month)
            transportation_outbound_data = transportation_outbound_data.filter(time__month=month)
            wh_outbound_data = wh_outbound_data.filter(time__month=month)
            returns_data = returns_data.filter(time__month=month)
            expiry_data = expiry_data.filter(time__month=month)
            damage_data = damage_data.filter(time__month=month)
            inventory_data = inventory_data.filter(time__month=month)
            pallet_location_availability_data = pallet_location_availability_data.filter(time__month=month)
            hse_data = hse_data.filter(time__month=month)

        if day:
            inbound_data = inbound_data.filter(time__day=day)
            transportation_outbound_data = transportation_outbound_data.filter(time__day=day)
            wh_outbound_data = wh_outbound_data.filter(time__day=day)
            returns_data = returns_data.filter(time__day=day)
            expiry_data = expiry_data.filter(time__day=day)
            damage_data = damage_data.filter(time__day=day)
            inventory_data = inventory_data.filter(time__day=day)
            pallet_location_availability_data = pallet_location_availability_data.filter(time__day=day)
            hse_data = hse_data.filter(time__day=day)

        # إضافة البيانات المفلترة إلى السياق
        context['inbound_data'] = inbound_data
        context['transportation_outbound_data'] = transportation_outbound_data
        context['wh_outbound_data'] = wh_outbound_data
        context['returns_data'] = returns_data
        context['expiry_data'] = expiry_data
        context['damage_data'] = damage_data
        context['inventory_data'] = inventory_data
        context['pallet_location_availability_data'] = pallet_location_availability_data
        context['hse_data'] = hse_data

        # Inbound
        context['inbound_data'] = inbound_data
        context['total_vehicles_daily'] = inbound_data.aggregate(Sum('number_of_vehicles_daily'))[
                                              'number_of_vehicles_daily__sum'] or 0
        context['total_pallets'] = inbound_data.aggregate(Sum('number_of_pallets'))['number_of_pallets__sum'] or 0
        context['total_pending_shipments'] = inbound_data.aggregate(Sum('pending_shipments'))[
                                                 'pending_shipments__sum'] or 0
        context['total_number_of_shipments'] = inbound_data.aggregate(Sum('number_of_shipments'))[
                                                   'number_of_shipments__sum'] or 0

        context['total_quantity'] = inbound_data.aggregate(Sum('total_quantity'))['total_quantity__sum'] or 0

        context['total_number_of_line'] = inbound_data.aggregate(Sum('number_of_line'))['number_of_line__sum'] or 0

        shipment_types = ['bulk', 'loose', 'cold', 'frozen', 'ambient']
        shipment_data = {
            stype: inbound_data.aggregate(Sum(stype))[stype + '__sum'] or 0
            for stype in shipment_types
        }
        context['shipment_data'] = shipment_data

        # الحصول على جميع بيانات Transportation Outbound_data
        context['transportation_outbound_data'] = transportation_outbound_data

        context['total_released_order'] = transportation_outbound_data.aggregate(Sum('released_order'))['released_order__sum'] or 0

        context['total_pending_pick_orders'] = transportation_outbound_data.aggregate(Sum('pending_pick_orders'))['pending_pick_orders__sum'] or 0

        context['total_piked_order'] = transportation_outbound_data.aggregate(Sum('piked_order'))['piked_order__sum'] or 0

        context['total_number_of_PODs_collected_on_time'] = transportation_outbound_data.aggregate(Sum('number_of_PODs_collected_on_time'))['number_of_PODs_collected_on_time__sum'] or 0

        context['total_number_of_PODs_collected_Late'] = transportation_outbound_data.aggregate(Sum('number_of_PODs_collected_Late'))['number_of_PODs_collected_Late__sum'] or 0



        # الحصول على جميع بيانات WH Outbound_data
        context['wh_outbound_data'] = wh_outbound_data
        context['total_released_order'] = wh_outbound_data.aggregate(Sum('released_order'))['released_order__sum'] or 0

        context['total_pending_pick_orders'] = wh_outbound_data.aggregate(Sum('pending_pick_orders'))['pending_pick_orders__sum'] or 0
        context['total_piked_order'] = wh_outbound_data.aggregate(Sum('piked_order'))['piked_order__sum'] or 0

        context['total_number_of_PODs_collected_on_time'] = \
            wh_outbound_data.aggregate(Sum('number_of_PODs_collected_on_time'))[
                'number_of_PODs_collected_on_time__sum'] or 0
        context['total_number_of_PODs_collected_Late'] = wh_outbound_data.aggregate(Sum('number_of_PODs_collected_Late'))[
                                                             'number_of_PODs_collected_Late__sum'] or 0


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
        total_expired_SKUS_disposed = expiry_data.aggregate(Sum('total_expired_SKUS_disposed'))[
                                          'total_expired_SKUS_disposed__sum'] or 0
        total_nearly_expired_1_to_3_months = expiry_data.aggregate(Sum('nearly_expired_1_to_3_months'))[
                                                 'nearly_expired_1_to_3_months__sum'] or 0
        total_nearly_expired_3_to_6_months = expiry_data.aggregate(Sum('nearly_expired_3_to_6_months'))[
                                                 'nearly_expired_3_to_6_months__sum'] or 0

        total_SKUs_expired_calculated = (
                total_expired_SKUS_disposed +
                total_nearly_expired_1_to_3_months +
                total_nearly_expired_3_to_6_months
        )

        context['expiry_data'] = expiry_data
        context['total_SKUs_expired'] = expiry_data.aggregate(Sum('total_SKUs_expired'))['total_SKUs_expired__sum'] or 0
        context['total_expired_SKUS_disposed'] = total_expired_SKUS_disposed
        context['total_nearly_expired_1_to_3_months'] = total_nearly_expired_1_to_3_months
        context['total_nearly_expired_3_to_6_months'] = total_nearly_expired_3_to_6_months
        context['total_SKUs_expired_calculated'] = total_SKUs_expired_calculated

        # Damage
        context['damage_data'] = damage_data
        context['Total_QTYs_Damaged_by_WH'] = damage_data.aggregate(Sum('Total_QTYs_Damaged_by_WH'))['Total_QTYs_Damaged_by_WH__sum'] or 0
        context['Total_Number_of_Damaged_during_receiving'] = damage_data.aggregate(Sum('Number_of_Damaged_during_receiving'))[
                'Number_of_Damaged_during_receiving__sum'] or 0
        context['Total_Araive_Damaged'] = damage_data.aggregate(Sum('Total_Araive_Damaged'))['Total_Araive_Damaged__sum'] or 0

        # Inventory
        context['inventory_data'] = inventory_data
        context['Total_Locations_match'] = inventory_data.aggregate(Sum('Total_Locations_match'))['Total_Locations_match__sum'] or 0
        context['Total_Locations_not_match'] = inventory_data.aggregate(Sum('Total_Locations_not_match'))['Total_Locations_not_match__sum'] or 0


        # PalletLocationAvailability
        context['pallet_location_availability_data'] = pallet_location_availability_data
        context['Total_Storage_Pallet'] = pallet_location_availability_data.aggregate(Sum('Total_Storage_Pallet'))[
                                              'Total_Storage_Pallet__sum'] or 0
        context['Total_Storage_pallet_empty'] = \
            pallet_location_availability_data.aggregate(Sum('Total_Storage_pallet_empty'))[
                'Total_Storage_pallet_empty__sum'] or 0

        context['Total_Storage_Bin'] = pallet_location_availability_data.aggregate(Sum('Total_Storage_Bin'))[
                                           'Total_Storage_Bin__sum'] or 0
        context['Total_occupied_pallet_location'] = \
            pallet_location_availability_data.aggregate(Sum('Total_occupied_pallet_location'))[
                'Total_occupied_pallet_location__sum'] or 0

        context['Total_Storage_Bin_empty'] = \
            pallet_location_availability_data.aggregate(Sum('Total_Storage_Bin_empty'))[
                'Total_Storage_Bin_empty__sum'] or 0
        context['Total_Storage_Bin_empty'] = \
            pallet_location_availability_data.aggregate(Sum('Total_Storage_Bin_empty'))[
                'Total_Storage_Bin_empty__sum'] or 0

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
class CustomerEditDataView(View):
    model_map = {
        'Customer': Customer,
        'CustomerInbound': CustomerInbound,
        'CustomerTransportationOutbound': CustomerTransportationOutbound,
        'CustomerWHOutbound': CustomerWHOutbound,
        'CustomerReturns': CustomerReturns,
        'CustomerExpiry': CustomerExpiry,
        'CustomerDamage': CustomerDamage,
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

        company = None
        if is_employee:
            company = EmployeeProfile.objects.filter(user=user).first().company
        elif is_customer:
            company = Customer.objects.filter(employees__user=user).first()

        if 'download' in request.GET:
            if request.GET.get('format') == 'pdf':
                return self.download_pdf(request)
            else:
                return self.download_excel(request, company)

        context = {
            "user": user,
            "user_type": "Employee" if is_employee else "Customer",  # تحديد نوع المستخدم هنا
            "is_admin": is_admin,
            "is_employee": is_employee,
            "is_customer": is_customer,
            "dashboard_choice": dashboard_choice,
            "company": company,  # إضافة الشركة إلى السياق
            "breadcrumb": {
                "title": "Admin Dashboard" if dashboard_choice == 'admin_dashboard' else "Customer Dashboard",
                "parent": "Edit Data",
                "child": "Default"
            }
        }

        if dashboard_choice == 'admin_dashboard' and is_admin:
            admin_data = AdminData.objects.all()
            context["admin_data"] = admin_data
        elif dashboard_choice == 'customer_dashboard' and company:
            companies = Customer.objects.filter(employees__user=user)
            inbounds = CustomerInbound.objects.filter(company=company)
            transportation_outbounds = CustomerTransportationOutbound.objects.filter(company=company)
            wh_outbounds = CustomerWHOutbound.objects.filter(company=company)
            returns = CustomerReturns.objects.filter(company=company)
            expiries = CustomerExpiry.objects.filter(company=company)
            damages = CustomerDamage.objects.filter(company=company)
            inventories = CustomerInventory.objects.filter(company=company)
            pallet_location_availabilities = CustomerPalletLocationAvailability.objects.filter(company=company)
            hses = CustomerHSE.objects.filter(company=company)

            context.update({
                "companies": companies,
                "inbounds": inbounds,
                "transportation_outbounds": transportation_outbounds,
                "wh_outbounds": wh_outbounds,
                "returns": returns,
                "expiries": expiries,
                "damages": damages,
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

    def download_excel(self, request, company):
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

        company = None
        if is_employee:
            company = EmployeeProfile.objects.filter(user=user).first().company
        elif is_customer:
            company = Customer.objects.filter(employees__user=user).first()

        # إعداد البيانات للتصدير إلى Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if dashboard_choice == 'admin_dashboard' and is_admin:
                admin_data = AdminData.objects.all().values()
                pd.DataFrame(list(admin_data)).to_excel(writer, sheet_name='AdminData')
            elif dashboard_choice == 'customer_dashboard' and company:
                companies = Customer.objects.filter(employees__user=user).values()
                inbounds = CustomerInbound.objects.filter(company=company).values()
                transportation_outbounds = CustomerTransportationOutbound.objects.filter(company=company).values()
                wh_outbounds = CustomerWHOutbound.objects.filter(company=company).values()
                returns = CustomerReturns.objects.filter(company=company).values()
                expiries = CustomerExpiry.objects.filter(company=company).values()
                damages = CustomerDamage.objects.filter(company=company).values()
                inventories = CustomerInventory.objects.filter(company=company).values()
                pallet_location_availabilities = CustomerPalletLocationAvailability.objects.filter(
                    company=company).values()
                hses = CustomerHSE.objects.filter(company=company).values()

                pd.DataFrame(list(companies)).to_excel(writer, sheet_name='Companies')
                pd.DataFrame(list(inbounds)).to_excel(writer, sheet_name='Inbounds')
                pd.DataFrame(list(transportation_outbounds)).to_excel(writer, sheet_name='TransportationOutbound')
                pd.DataFrame(list(wh_outbounds)).to_excel(writer, sheet_name='WHOutbound')
                pd.DataFrame(list(returns)).to_excel(writer, sheet_name='Returns')
                pd.DataFrame(list(expiries)).to_excel(writer, sheet_name='Expiries')
                pd.DataFrame(list(damages)).to_excel(writer, sheet_name='Damages')
                pd.DataFrame(list(inventories)).to_excel(writer, sheet_name='Inventories')
                pd.DataFrame(list(pallet_location_availabilities)).to_excel(writer,
                                                                            sheet_name='PalletLocationAvailabilities')
                pd.DataFrame(list(hses)).to_excel(writer, sheet_name='HSEs')

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=data.xlsx'
        response.write(output.getvalue())
        return response

    def download_pdf(self, request):
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

        company = None
        if is_employee:
            company = EmployeeProfile.objects.filter(user=user).first().company
        elif is_customer:
            company = Customer.objects.filter(employees__user=user).first()

        if not company:
            return HttpResponseBadRequest("Company not found for current user.")

        # Example: Fetching data related to the company for PDF generation
        companies = Customer.objects.filter(employees__company=company)
        inbounds = CustomerInbound.objects.filter(company=company)
        transportation_outbounds = CustomerTransportationOutbound.objects.filter(company=company)
        wh_outbounds = CustomerWHOutbound.objects.filter(company=company)
        returns = CustomerReturns.objects.filter(company=company)
        expiries = CustomerExpiry.objects.filter(company=company)
        damages = CustomerDamage.objects.filter(company=company)
        inventories = CustomerInventory.objects.filter(company=company)
        pallet_location_availabilities = CustomerPalletLocationAvailability.objects.filter(company=company)
        hses = CustomerHSE.objects.filter(company=company)

        # Generating PDF using reportlab
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=data-customer.pdf'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        data_sets = [
            ('Companies', companies),
            ('Inbounds', inbounds),
            ('TransportationOutbound', transportation_outbounds),
            ('WHOutbounds', wh_outbounds),
            ('Returns', returns),
            ('Expiries', expiries),
            ('Damages', damages),
            ('Inventories', inventories),
            ('Pallet Location Availabilities', pallet_location_availabilities),
            ('HSEs', hses)
        ]

        styles = getSampleStyleSheet()
        heading_style = styles['Heading1']
        normal_style = styles['Normal']

        for title, data in data_sets:
            # Add caption before each table
            caption_text = f"<b>{title}</b>"
            caption = Paragraph(caption_text, heading_style)
            elements.append(caption)

            # Prepare table data
            data_list = [[key, value] for item in data.values() for key, value in item.items()]
            table = Table(data_list, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(0, 20))  # Add space after each table

        doc.build(elements)
        return response


### Add Data Form Customer
def is_employee(user):
    return user.groups.filter(name='Employee').exists()


@method_decorator([login_required, user_passes_test(is_employee)], name='dispatch')
class AddCustomerDataView(View):
    def get(self, request):
        current_user = request.user
        user_type = ''
        company = None

        if request.user.groups.filter(name='Super Admin').exists():
            user_type = 'Super Admin'
        elif request.user.groups.filter(name='Admin').exists():
            user_type = 'Admin'
        elif request.user.groups.filter(name='Employee').exists():
            user_type = 'Employee'
            company = EmployeeProfile.objects.filter(user=request.user).first().company
        elif request.user.groups.filter(name='Customer').exists():
            user_type = 'Customer'
            company = Customer.objects.filter(employees__user=request.user).first()
        else:
            user_type = 'Unknown'

        context = {
            'customer_form': CustomerForm(user=request.user),  # Pass current user to form
            'customer_inbound_form': CustomerInboundForm(),
            'customer_transportation_outbound_form': CustomerTransportationOutboundForm(),
            'customer_wh_outbound_form': CustomerWHOutboundForm(),
            'customer_returns_form': CustomerReturnsForm(),
            'customer_expiry_form': CustomerExpiryForm(),
            'customer_damage_form': CustomerDamageForm(),
            'customer_inventory_form': CustomerInventoryForm(),
            'customer_pallet_location_availability_form': CustomerPalletLocationAvailabilityForm(),
            'customer_hse_form': CustomerHSEForm(),
            'current_user': current_user.username,  # Add current user's username to context
            'company_name': company.name_company if company else '',  # Add company name to context
            'user_type': user_type,  # Add user type to context
            'breadcrumb': {
                'title': 'Employee Dashboard',
                'parent': 'Edit Data',
                'child': 'Default'
            }
        }
        return render(request, 'general/dashboard/default/components/add_admin_data.html', context)

    def post(self, request):
        customer_form = CustomerForm(request.POST, user=request.user)
        customer_inbound_form = CustomerInboundForm(request.POST)
        customer_transportation_outbound_form = CustomerTransportationOutboundForm(request.POST)
        customer_wh_outbound_form = CustomerWHOutboundForm(request.POST)
        customer_returns_form = CustomerReturnsForm(request.POST)
        customer_expiry_form = CustomerExpiryForm(request.POST)
        customer_damage_form = CustomerDamageForm(request.POST)
        customer_inventory_form = CustomerInventoryForm(request.POST)
        customer_pallet_location_availability_form = CustomerPalletLocationAvailabilityForm(request.POST)
        customer_hse_form = CustomerHSEForm(request.POST)

        forms = [
            customer_form,
            customer_inbound_form,
            customer_transportation_outbound_form,
            customer_wh_outbound_form,
            customer_returns_form,
            customer_expiry_form,
            customer_damage_form,
            customer_inventory_form,
            customer_pallet_location_availability_form,
            customer_hse_form
        ]

        if all(form.is_valid() for form in forms):
            try:
                with transaction.atomic():
                    customer_data = customer_form.save(commit=False)
                    customer_data.user = request.user  # Assign the current user

                    company = None
                    if request.user.groups.filter(name='Employee').exists():
                        company = EmployeeProfile.objects.filter(user=request.user).first().company
                    elif request.user.groups.filter(name='Customer').exists():
                        company = Customer.objects.filter(employees__user=request.user).first()

                    customer_data.company = company  # Assign the company
                    customer_data.save()

                    # Assign the company to all related forms
                    customer_inbound_form.instance.customer = customer_data
                    customer_inbound_form.instance.company = company
                    customer_transportation_outbound_form.instance.customer = customer_data
                    customer_transportation_outbound_form.instance.company = company
                    customer_wh_outbound_form.instance.customer = customer_data
                    customer_wh_outbound_form.instance.company = company
                    customer_returns_form.instance.customer = customer_data
                    customer_returns_form.instance.company = company
                    customer_expiry_form.instance.customer = customer_data
                    customer_expiry_form.instance.company = company
                    customer_damage_form.instance.customer = customer_data
                    customer_damage_form.instance.company = company
                    customer_inventory_form.instance.customer = customer_data
                    customer_inventory_form.instance.company = company
                    customer_pallet_location_availability_form.instance.customer = customer_data
                    customer_pallet_location_availability_form.instance.company = company
                    customer_hse_form.instance.customer = customer_data
                    customer_hse_form.instance.company = company

                    customer_inbound_form.save()
                    customer_transportation_outbound_form.save()
                    customer_wh_outbound_form.save()
                    customer_returns_form.save()
                    customer_expiry_form.save()
                    customer_damage_form.save()
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