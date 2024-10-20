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
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


from .forms import AdminDataForm, AdminInboundForm, AdminOutboundForm, \
    AdminReturnsForm, AdminCapacityForm, AdminInventoryForm
from .models import AdminInbound, AdminOutbound, AdminReturns, AdminCapacity, AdminInventory, AdminData, \
    EmployeeProfile


#### View Dashborad Admin
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_user = self.request.user

        # Filter AdminData entries by current user
        admin_data_entries = AdminData.objects.filter(user=current_user)

        context['admin_data_entries'] = admin_data_entries
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
            inbound_data = inbound_data.filter(admin_data__company__hc_business=hc_business)
            outbound_data = outbound_data.filter(admin_data__company__hc_business=hc_business)
            returns_data = returns_data.filter(admin_data__company__hc_business=hc_business)
            capacity_data = capacity_data.filter(admin_data__company__hc_business=hc_business)
            inventory_data = inventory_data.filter(admin_data__company__hc_business=hc_business)

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

        # Inbound
        context['total_vehicles_daily'] = inbound_data.aggregate(Sum('number_of_vehicles_daily'))[
                                              'number_of_vehicles_daily__sum'] or 0
        context['total_pallets'] = inbound_data.aggregate(Sum('number_of_pallets'))['number_of_pallets__sum'] or 0
        context['total_pending_shipments'] = inbound_data.aggregate(Sum('pending_shipments'))[
                                                 'pending_shipments__sum'] or 0
        context['total_number_of_shipments'] = inbound_data.aggregate(Sum('number_of_shipments'))['number_of_shipments__sum'] or 0

        context['total_quantity'] = inbound_data.aggregate(Sum('total_quantity'))['total_quantity__sum'] or 0

        context['total_number_of_line'] = inbound_data.aggregate(Sum('number_of_line'))['number_of_line__sum'] or 0

        shipment_types = ['bulk', 'loose', 'cold', 'frozen', 'ambient']
        shipment_data = {
            stype: inbound_data.aggregate(Sum(stype))[stype + '__sum'] or 0
            for stype in shipment_types
        }
        context['shipment_data'] = shipment_data

        # Outbound
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

        # Capacity
        context['WH_storage'] = capacity_data.aggregate(Sum('WH_storage'))['WH_storage__sum'] or 0
        context['occupied_location'] = capacity_data.aggregate(Sum('occupied_location'))['occupied_location__sum'] or 0
        context['available_location'] = capacity_data.aggregate(Sum('available_location'))['available_location__sum'] or 0

        # Returns
        context['total_number_of_return'] = returns_data.aggregate(Sum('number_of_return'))['number_of_return__sum'] or 0
        context['total_number_of_lines'] = returns_data.aggregate(Sum('number_of_lines'))['number_of_lines__sum'] or 0
        context['total_quantities'] = returns_data.aggregate(Sum('total_quantities'))['total_quantities__sum'] or 0

        # Inventory
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
        businesses = AdminData.objects.values_list('company__hc_business', flat=True).distinct()

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

def is_employee(user):
    return user.groups.filter(name='Employee').exists()


def is_customer(user):
    return user.groups.filter(name='Customer').exists()


def is_employee(user):
    return user.groups.filter(name='Employee').exists()


@method_decorator([login_required, csrf_exempt], name='dispatch')
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

        if 'download' in request.GET:
            if request.GET.get('format') == 'pdf':
                return self.download_pdf(request)
            else:
                return self.download_excel(request)

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
            admin_data = AdminData.objects.filter(company=EmployeeProfile.objects.get(user=user).company)
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

    def download_excel(self, request):
        user = request.user
        is_employee = self.is_employee_user(user)

        # جلب البيانات المراد تحميلها
        admin_data = AdminData.objects.filter(company=EmployeeProfile.objects.get(user=user).company)
        admin_inbound_data = AdminInbound.objects.filter(admin_data__in=admin_data)
        admin_outbound_data = AdminOutbound.objects.filter(admin_data__in=admin_data)
        admin_returns_data = AdminReturns.objects.filter(admin_data__in=admin_data)
        admin_capacity_data = AdminCapacity.objects.filter(admin_data__in=admin_data)
        admin_inventory_data = AdminInventory.objects.filter(admin_data__in=admin_data)

        # إعداد البيانات للتصدير إلى Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(list(admin_data.values())).to_excel(writer, sheet_name='AdminData')
            pd.DataFrame(list(admin_inbound_data.values())).to_excel(writer, sheet_name='AdminInbound')
            pd.DataFrame(list(admin_outbound_data.values())).to_excel(writer, sheet_name='AdminOutbound')
            pd.DataFrame(list(admin_returns_data.values())).to_excel(writer, sheet_name='AdminReturns')
            pd.DataFrame(list(admin_capacity_data.values())).to_excel(writer, sheet_name='AdminCapacity')
            pd.DataFrame(list(admin_inventory_data.values())).to_excel(writer, sheet_name='AdminInventory')

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=admin_data.xlsx'
        response.write(output.getvalue())
        return response

    def download_pdf(self, request):
        user = request.user
        is_employee = self.is_employee_user(user)

        # جلب البيانات المراد تحميلها
        admin_data = AdminData.objects.filter(company=EmployeeProfile.objects.get(user=user).company)
        admin_inbound_data = AdminInbound.objects.filter(admin_data__in=admin_data)
        admin_outbound_data = AdminOutbound.objects.filter(admin_data__in=admin_data)
        admin_returns_data = AdminReturns.objects.filter(admin_data__in=admin_data)
        admin_capacity_data = AdminCapacity.objects.filter(admin_data__in=admin_data)
        admin_inventory_data = AdminInventory.objects.filter(admin_data__in=admin_data)

        # إعداد ملف PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=admin_data.pdf'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        # تخصيص الأنماط
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=20
        )

        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            textColor=colors.black,
            spaceAfter=10
        )

        data_sets = [
            ('AdminData', admin_data),
            ('AdminInbound', admin_inbound_data),
            ('AdminOutbound', admin_outbound_data),
            ('AdminReturns', admin_returns_data),
            ('AdminCapacity', admin_capacity_data),
            ('AdminInventory', admin_inventory_data)
        ]

        for title, data in data_sets:
            # إضافة العنوان
            elements.append(Paragraph(f"{title}", heading_style))

            # إعداد البيانات كجدول
            if data.exists():  # تحقق مما إذا كان هناك بيانات
                data_list = [[key for key in data.values()[0].keys()]]  # إضافة العناوين كصف أول
                for item in data.values():
                    data_list.append([value for value in item.values()])  # إضافة القيم

                table = Table(data_list)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),  # تخصيص الخط
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # تغيير لون النص في الصفوف
                ]))
                elements.append(table)
            else:
                elements.append(Paragraph(f"No data available for {title}.", normal_style))

            elements.append(Spacer(0, 20))  # إضافة مساحة بعد كل جدول

        doc.build(elements)
        return response


def is_employee(user):
    return user.groups.filter(name='Employee').exists()

@method_decorator([login_required, user_passes_test(is_employee)], name='dispatch')
class AddAdminDataView(View):
    def get(self, request):
        try:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            company_name = employee_profile.company.hc_business
            user_type = "Employee"

            admin_data_form = AdminDataForm(user=request.user)
            admin_inbound_form = AdminInboundForm()
            admin_outbound_form = AdminOutboundForm()
            admin_returns_form = AdminReturnsForm()
            admin_capacity_form = AdminCapacityForm()
            admin_inventory_form = AdminInventoryForm()

        except EmployeeProfile.DoesNotExist:
            company_name = None
            user_type = "Unknown"
            admin_data_form = AdminDataForm()
            admin_inbound_form = AdminInboundForm()
            admin_outbound_form = AdminOutboundForm()
            admin_returns_form = AdminReturnsForm()
            admin_capacity_form = AdminCapacityForm()
            admin_inventory_form = AdminInventoryForm()

        context = {
            'admin_data_form': admin_data_form,
            'admin_inbound_form': admin_inbound_form,
            'admin_outbound_form': admin_outbound_form,
            'admin_returns_form': admin_returns_form,
            'admin_capacity_form': admin_capacity_form,
            'admin_inventory_form': admin_inventory_form,
            'current_user': request.user.username,
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
        admin_data_form = AdminDataForm(request.POST, user=request.user)
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
            admin_inventory_form,
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
                return redirect('accounts:admin_dashboard')

            except Exception as e:
                messages.error(request, f'Failed to save admin data. Error: {str(e)}')

        else:
            for form in forms:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)

        return redirect('administration:add_admin_data')
