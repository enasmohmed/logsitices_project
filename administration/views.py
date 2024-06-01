from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView

from .models import Inbound, Outbound, Returns, Capacity, Inventory, AdminData


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # بيانات فتات الخبز
        context['breadcrumb'] = {
            "title": "Dashboard For Admin",
            "parent": "Dashboard",
            "child": "Default"
        }

        # Inbound Model and Sum Total data
        inbound_data = Inbound.objects.all()
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

        # Outbound Model and Sum Total data
        outbound_data = Outbound.objects.all()
        context['tender_sum'] = outbound_data.aggregate(Sum('tender'))['tender__sum'] or 0
        context['private_sum'] = outbound_data.aggregate(Sum('private'))['private__sum'] or 0
        context['bulk_sum'] = outbound_data.aggregate(Sum('bulk'))['bulk__sum'] or 0
        context['loose_sum'] = outbound_data.aggregate(Sum('loose'))['loose__sum'] or 0
        context['lines_sum'] = outbound_data.aggregate(Sum('lines'))['lines__sum'] or 0
        context['total_quantities_sum'] = outbound_data.aggregate(Sum('total_quantities'))['total_quantities__sum'] or 0
        context['pending_orders_sum'] = outbound_data.aggregate(Sum('pending_orders'))['pending_orders__sum'] or 0

        # Add Name Chart Dashboard
        context['chart_name_tender'] = 'Tender'
        context['chart_name_private'] = 'Private'
        context['chart_name_bulk'] = 'Bulk'
        context['chart_name_loose'] = 'Loose'

        # Capacity Model and Sum Total data
        capacity_data = Capacity.objects.all()
        context['total_capacity'] = capacity_data.aggregate(Sum('total_available_locations_and_accupied'))[
                                        'total_available_locations_and_accupied__sum'] or 0

        # Returns Model and Sum Total data
        returns_data = Returns.objects.all()
        context['total_no_of_return'] = returns_data.aggregate(Sum('no_of_return'))['no_of_return__sum'] or 0
        context['total_no_of_lines'] = returns_data.aggregate(Sum('no_of_lines'))['no_of_lines__sum'] or 0
        context['total_quantities'] = returns_data.aggregate(Sum('total_quantities'))['total_quantities__sum'] or 0

        # Inventory Model and Sum Total data
        inventory_data = Inventory.objects.all()
        context['total_last_movement'] = inventory_data.aggregate(Sum('last_movement'))['last_movement__sum'] or 0

        # Filter Years and Day and time
        # الحصول على معايير التصفية من الطلب
        selected_year = self.request.GET.get('year')
        selected_month = self.request.GET.get('month')
        selected_day = self.request.GET.get('day')
        hc_business = self.request.GET.get('hc_business')

        # تصفية البيانات بناءً على المعايير المحددة
        filtered_inbound = Inbound.objects.all()
        filtered_outbound = Outbound.objects.all()
        filtered_returns = Returns.objects.all()
        filtered_capacity = Capacity.objects.all()
        filtered_inventory = Inventory.objects.all()

        if selected_year:
            filtered_inbound = filtered_inbound.filter(time__year=selected_year)
            filtered_outbound = filtered_outbound.filter(time__year=selected_year)
            filtered_returns = filtered_returns.filter(time__year=selected_year)
            filtered_capacity = filtered_capacity.filter(time__year=selected_year)
            filtered_inventory = filtered_inventory.filter(time__year=selected_year)

        if selected_month:
            filtered_inbound = filtered_inbound.filter(time__month=selected_month)
            filtered_outbound = filtered_outbound.filter(time__month=selected_month)
            filtered_returns = filtered_returns.filter(time__month=selected_month)
            filtered_capacity = filtered_capacity.filter(time__month=selected_month)
            filtered_inventory = filtered_inventory.filter(time__month=selected_month)

        if selected_day:
            filtered_inbound = filtered_inbound.filter(time__day=selected_day)
            filtered_outbound = filtered_outbound.filter(time__day=selected_day)
            filtered_returns = filtered_returns.filter(time__day=selected_day)
            filtered_capacity = filtered_capacity.filter(time__day=selected_day)
            filtered_inventory = filtered_inventory.filter(time__day=selected_day)

        if hc_business:
            filtered_inbound = filtered_inbound.filter(admin_data__hc_business=hc_business)
            filtered_outbound = filtered_outbound.filter(admin_data__hc_business=hc_business)
            filtered_returns = filtered_returns.filter(admin_data__hc_business=hc_business)
            filtered_capacity = filtered_capacity.filter(admin_data__hc_business=hc_business)
            filtered_inventory = filtered_inventory.filter(admin_data__hc_business=hc_business)

        # احتساب عدد السنين، الشهور، والأيام
        year_count = Inbound.objects.dates('time', 'year').count()
        month_count = Inbound.objects.dates('time', 'month').count()
        day_count = Inbound.objects.dates('time', 'day').count()

        # الحصول على جميع السنين والشهور والأيام
        years = Inbound.objects.dates('time', 'year')
        months = Inbound.objects.dates('time', 'month')
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # الحصول على جميع أسماء الشركات من AdminData
        businesses = AdminData.objects.values_list('hc_business', flat=True).distinct()

        context.update({
            'year_count': year_count,
            'month_count': month_count,
            'day_count': day_count,
            'filtered_inbound': filtered_inbound,
            'filtered_outbound': filtered_outbound,
            'filtered_returns': filtered_returns,
            'filtered_capacity': filtered_capacity,
            'filtered_inventory': filtered_inventory,
            'years': years,
            'months': months,
            'days': days,
            'businesses': businesses,
        })

        return context
