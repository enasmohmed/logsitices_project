import calendar
import json
from io import BytesIO

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

from accounts.forms import AdminDataForm, AdminInboundForm, AdminOutboundForm, AdminReturnsForm, AdminCapacityForm, \
    AdminInventoryForm
from .models import AdminInbound, AdminOutbound, AdminReturns, AdminCapacity, AdminInventory, AdminData, EmployeeProfile


#### View Dashborad Admin
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['breadcrumb'] = {
            "title": "Healthcare Dashboard",
            "parent": "Dashboard",
            "child": "Default"
        }

        hc_business = self.request.GET.get('hc_business')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        day = self.request.GET.get('day')

        # Retrieve all data without role-specific filters
        inbound_data = AdminInbound.objects.all()
        outbound_data = AdminOutbound.objects.all()
        returns_data = AdminReturns.objects.all()
        capacity_data = AdminCapacity.objects.all()
        inventory_data = AdminInventory.objects.all()

        # Apply optional filters based on query parameters
        if hc_business:
            inbound_data = inbound_data.filter(admin_data__hc_business=hc_business)
            outbound_data = outbound_data.filter(admin_data__hc_business=hc_business)
            returns_data = returns_data.filter(admin_data__hc_business=hc_business)
            capacity_data = capacity_data.filter(admin_data__hc_business=hc_business)
            inventory_data = inventory_data.filter(admin_data__hc_business=hc_business)

        if year:
            inbound_data = inbound_data.filter(time__year=year)
            outbound_data = outbound_data.filter(time__year=year)
            returns_data = returns_data.filter(time__year=year)
            capacity_data = capacity_data.filter(time__year=year)
            inventory_data = inventory_data.filter(time__year=year)

        if month:
            inbound_data = inbound_data.filter(time__month=month)
            outbound_data = outbound_data.filter(time__month=month)
            returns_data = returns_data.filter(time__month=month)
            capacity_data = capacity_data.filter(time__month=month)
            inventory_data = inventory_data.filter(time__month=month)

        if day:
            inbound_data = inbound_data.filter(time__day=day)
            outbound_data = outbound_data.filter(time__day=day)
            returns_data = returns_data.filter(time__day=day)
            capacity_data = capacity_data.filter(time__day=day)
            inventory_data = inventory_data.filter(time__day=day)

        # Calculate total statistics for filtered data
        context['total_vehicles_daily'] = inbound_data.aggregate(Sum('number_of_vehicles_daily'))[
                                              'number_of_vehicles_daily__sum'] or 0
        context['total_pallets'] = inbound_data.aggregate(Sum('number_of_pallets'))['number_of_pallets__sum'] or 0
        context['total_pending_shipments'] = inbound_data.aggregate(Sum('pending_shipments'))[
                                                 'pending_shipments__sum'] or 0
        context['total_no_of_shipments'] = inbound_data.aggregate(Sum('no_of_shipments'))['no_of_shipments__sum'] or 0

        shipment_types = ['bulk', 'mix', 'cold', 'frozen', 'ambient']
        shipment_data = {
            stype: inbound_data.aggregate(Sum(stype))[stype + '__sum'] or 0
            for stype in shipment_types
        }
        context['shipment_data'] = shipment_data

        context['tender_sum'] = outbound_data.aggregate(Sum('tender'))['tender__sum'] or 0
        context['private_sum'] = outbound_data.aggregate(Sum('private'))['private__sum'] or 0
        context['bulk_sum'] = outbound_data.aggregate(Sum('bulk'))['bulk__sum'] or 0
        context['loose_sum'] = outbound_data.aggregate(Sum('loose'))['loose__sum'] or 0
        context['lines_sum'] = outbound_data.aggregate(Sum('lines'))['lines__sum'] or 0
        context['total_quantities_sum'] = outbound_data.aggregate(Sum('total_quantities'))['total_quantities__sum'] or 0
        context['pending_orders_sum'] = outbound_data.aggregate(Sum('pending_orders'))['pending_orders__sum'] or 0

        context['chart_name_tender'] = 'Tender'
        context['chart_name_private'] = 'Private'
        context['chart_name_bulk'] = 'Bulk'
        context['chart_name_loose'] = 'Loose'

        context['total_capacity'] = capacity_data.aggregate(Sum('total_available_locations_and_accupied'))[
                                        'total_available_locations_and_accupied__sum'] or 0

        context['total_no_of_return'] = returns_data.aggregate(Sum('no_of_return'))['no_of_return__sum'] or 0
        context['total_no_of_lines'] = returns_data.aggregate(Sum('no_of_lines'))['no_of_lines__sum'] or 0
        context['total_quantities'] = returns_data.aggregate(Sum('total_quantities'))['total_quantities__sum'] or 0

        context['total_last_movement'] = inventory_data.aggregate(Sum('last_movement'))['last_movement__sum'] or 0

        # Calculate count of years, months, and days
        year_count = AdminInbound.objects.dates('time', 'year').count()
        month_count = AdminInbound.objects.dates('time', 'month').count()
        day_count = AdminInbound.objects.dates('time', 'day').count()

        # Get all years, months, and days
        years = AdminInbound.objects.dates('time', 'year')
        months = list(calendar.month_name)[1:]
        days = range(1, 32)  # Get days of the month

        # Get all company names from AdminData
        businesses = AdminData.objects.values_list('hc_business', flat=True).distinct()

        context.update({
            'year_count': year_count,
            'month_count': month_count,
            'day_count': day_count,
            'years': years,
            'months': months,
            'days': days,
            'businesses': businesses,
            'filtered_inbound': inbound_data,
            'filtered_outbound': outbound_data,
            'filtered_returns': returns_data,
            'filtered_capacity': capacity_data,
            'filtered_inventory': inventory_data,
            'hc_business': hc_business,
            'selected_year': year,
            'selected_month': month,
            'selected_day': day,
        })

        # Determine user_type based on user roles
        if self.request.user.is_superuser:
            context['user_type'] = "Super Admin"
        elif self.request.user.groups.filter(name='Admin').exists():
            context['user_type'] = "Admin"
        elif self.request.user.groups.filter(name='Employee').exists():
            context['user_type'] = "Employee"
        else:
            context['user_type'] = "Unknown"

        return context


#### Edit Data Dashboard Admin
class AdminEditDataView(View):
    model_map = {
        'AdminData': AdminData,
        'AdminInbound': AdminInbound,
        'AdminOutbound': AdminOutbound,
        'AdminReturns': AdminReturns,
        'AdminCapacity': AdminCapacity,
        'AdminInventory': AdminInventory
    }

    def is_employee_user(self, user):
        return user.groups.filter(name='Employee').exists()

    def is_customer_user(self, user):
        return user.groups.filter(name='Customer').exists()

    def has_permission(self, user, model_instance):
        if self.is_employee_user(user) or user.is_staff:
            return True
        return user == model_instance.user

    @method_decorator(login_required, name='dispatch')
    @method_decorator(csrf_exempt, name='dispatch')
    def get(self, request):
        user = request.user
        is_admin = user.is_staff
        is_employee = self.is_employee_user(user)
        is_customer = self.is_customer_user(user)

        dashboard_choice = request.session.get('dashboard_choice', 'admin')

        if dashboard_choice not in ['admin', 'customer']:
            dashboard_choice = 'admin'

        if dashboard_choice == 'customer' and not (is_customer or is_employee):
            return HttpResponseForbidden("You do not have permission to access this page.")

        user_type = 'employee' if is_employee else 'customer'

        context = {
            "user": user,
            "is_admin": is_admin,
            "is_employee": is_employee,
            "is_customer": is_customer,
            "dashboard_choice": dashboard_choice,
            "user_type": user_type,
            "breadcrumb": {
                "title": "Admin Dashboard" if dashboard_choice == 'admin' else "Customer Dashboard",
                "parent": "Edit Data",
                "child": "Default"
            }
        }

        if is_admin or (is_employee and dashboard_choice == 'admin'):
            admin_data = AdminData.objects.filter(employees=user) if is_employee else AdminData.objects.filter(
                user=user)
            admin_inbound_data = AdminInbound.objects.filter(admin_data__in=admin_data)
            admin_outbound_data = AdminOutbound.objects.filter(admin_data__in=admin_data)
            admin_returns_data = AdminReturns.objects.filter(admin_data__in=admin_data)
            admin_capacity_data = AdminCapacity.objects.filter(admin_data__in=admin_data)
            admin_inventory_data = AdminInventory.objects.filter(admin_data__in=admin_data)

            context.update({
                "admin_data": admin_data,
                "admin_inbound_data": admin_inbound_data,
                "admin_outbound_data": admin_outbound_data,
                "admin_returns_data": admin_returns_data,
                "admin_capacity_data": admin_capacity_data,
                "admin_inventory_data": admin_inventory_data
            })

        return render(request, "excel.html", context)

    @method_decorator(login_required, name='dispatch')
    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        user = request.user
        is_admin = user.is_staff
        is_employee = self.is_employee_user(user)
        is_customer = self.is_customer_user(user)

        dashboard_choice = request.session.get('dashboard_choice', 'admin')

        if dashboard_choice not in ['admin', 'customer']:
            dashboard_choice = 'admin'

        if dashboard_choice == 'customer' and not (is_customer or is_employee):
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

                if not self.has_permission(user, obj):
                    return JsonResponse({"success": False, "error": "Permission denied."})

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

                if not self.has_permission(user, obj):
                    return JsonResponse({"success": False, "error": "Permission denied."})

                obj.delete()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Invalid model"})

        return JsonResponse({"success": False, "error": "Invalid operation"})

    @method_decorator(login_required)
    def download_excel(self, request):
        user = request.user
        is_admin = user.is_staff
        is_employee = self.is_employee_user(user)
        is_customer = self.is_customer_user(user)

        dashboard_choice = request.session.get('dashboard_choice', 'admin_dashboard')

        if dashboard_choice not in ['admin_dashboard', 'customer_dashboard']:
            dashboard_choice = 'admin_dashboard'

        if dashboard_choice == 'customer_dashboard' and not (is_customer or is_employee):
            return HttpResponseForbidden("You do not have permission to access this page.")

        if dashboard_choice == 'admin_dashboard' and not is_admin:
            return HttpResponseForbidden("You do not have permission to access this page.")

        # إعداد البيانات للتصدير إلى Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if dashboard_choice == 'admin_dashboard' and is_admin:
                admin_data = AdminData.objects.all().values()
                inbound_data = AdminInbound.objects.all().values()
                outbound_data = AdminOutbound.objects.all().values()
                returns_data = AdminReturns.objects.all().values()
                capacity_data = AdminCapacity.objects.all().values()
                inventory_data = AdminInventory.objects.all().values()

                pd.DataFrame(list(admin_data)).to_excel(writer, sheet_name='AdminData')
                pd.DataFrame(list(inbound_data)).to_excel(writer, sheet_name='InboundData')
                pd.DataFrame(list(outbound_data)).to_excel(writer, sheet_name='OutboundData')
                pd.DataFrame(list(returns_data)).to_excel(writer, sheet_name='ReturnsData')
                pd.DataFrame(list(capacity_data)).to_excel(writer, sheet_name='CapacityData')
                pd.DataFrame(list(inventory_data)).to_excel(writer, sheet_name='InventoryData')

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=admin_data.xlsx'
        response.write(output.getvalue())
        return response

    @method_decorator(login_required)
    def download_pdf(self, request):
        user = request.user
        is_admin = user.is_staff
        is_employee = self.is_employee_user(user)
        is_customer = self.is_customer_user(user)

        dashboard_choice = request.session.get('dashboard_choice', 'admin')

        if dashboard_choice not in ['admin_dashboard', 'customer_dashboard']:
            dashboard_choice = 'admin_dashboard'

        if dashboard_choice == 'admin_dashboard' and not is_admin:
            return HttpResponseForbidden("You do not have permission to access this page.")

        if dashboard_choice == 'customer_dashboard' and not (is_customer or is_employee):
            return HttpResponseForbidden("You do not have permission to access this page.")

        # Example: Fetching data related to Admin for PDF generation
        admin_data = AdminData.objects.all()
        admin_inbound_data = AdminInbound.objects.all()
        admin_outbound_data = AdminOutbound.objects.all()
        admin_returns_data = AdminReturns.objects.all()
        admin_capacity_data = AdminCapacity.objects.all()
        admin_inventory_data = AdminInventory.objects.all()

        # Generating PDF using reportlab
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="admin_data.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        data_sets = [
            ('Admin Data', admin_data),
            ('Admin Inbound Data', admin_inbound_data),
            ('Admin Outbound Data', admin_outbound_data),
            ('Admin Returns Data', admin_returns_data),
            ('Admin Capacity Data', admin_capacity_data),
            ('Admin Inventory Data', admin_inventory_data),
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


def download_excel_view(request):
    view = AdminEditDataView()
    return view.download_excel(request)


def download_pdf_view(request):
    view = AdminEditDataView()
    return view.download_pdf(request)


def is_employee(user):
    return user.groups.filter(name='Employee').exists()


### Add Data Form Admin


def is_employee(user):
    return user.groups.filter(name='Employee').exists()


@method_decorator([login_required, user_passes_test(is_employee)], name='dispatch')
class AddAdminDataView(View):
    def get(self, request):
        current_user = request.user.username
        user_type = ''

        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            company_name = employee_profile.company.hc_business
        except EmployeeProfile.DoesNotExist:
            company_name = None

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
            'admin_data_form': AdminDataForm(initial={'user': request.user}),
            'admin_inbound_form': AdminInboundForm(),
            'admin_outbound_form': AdminOutboundForm(),
            'admin_returns_form': AdminReturnsForm(),
            'admin_capacity_form': AdminCapacityForm(),
            'admin_inventory_form': AdminInventoryForm(),
            'current_user': current_user,
            'user_type': user_type,
            'company_name': company_name,
            'breadcrumb': {
                'title': 'Employee Dashboard',
                'parent': 'Edit Data',
                'child': 'Default'
            }
        }
        return render(request, 'general/dashboard/default/components/add_admin_data.html', context)

    def post(self, request):
        admin_data_form = AdminDataForm(request.POST)
        admin_inbound_form = AdminInboundForm(request.POST)
        admin_outbound_form = AdminOutboundForm(request.POST)
        admin_returns_form = AdminReturnsForm(request.POST)
        admin_capacity_form = AdminCapacityForm(request.POST)
        admin_inventory_form = AdminInventoryForm(request.POST)

        forms = [
            admin_data_form,
            admin_inbound_form,
            admin_outbound_form,
            admin_returns_form,
            admin_capacity_form,
            admin_inventory_form
        ]

        if all(form.is_valid() for form in forms):
            try:
                with transaction.atomic():
                    admin_data = admin_data_form.save(commit=False)
                    admin_data.user = request.user
                    admin_data.company = EmployeeProfile.objects.get(user=request.user).company
                    admin_data.save()

                    admin_inbound_form.instance.admin_data = admin_data
                    admin_outbound_form.instance.admin_data = admin_data
                    admin_returns_form.instance.admin_data = admin_data
                    admin_capacity_form.instance.admin_data = admin_data
                    admin_inventory_form.instance.admin_data = admin_data

                    admin_inbound_form.save()
                    admin_outbound_form.save()
                    admin_returns_form.save()
                    admin_capacity_form.save()
                    admin_inventory_form.save()

                messages.success(request, 'Admin data added successfully.')
                return redirect('accounts:employee_dashboard')

            except Exception as e:
                messages.error(request, f'Failed to save admin data. Error: {str(e)}')
                return redirect('accounts:add_admin_data')

        else:
            for form in forms:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)

            return redirect('accounts:add_admin_data')
