import calendar

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

        # الحصول على معايير التصفية من الطلب
        hc_business = self.request.GET.get('hc_business')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        day = self.request.GET.get('day')

        # تصفية البيانات بناءً على المعايير المحددة
        inbound_data = Inbound.objects.all()
        outbound_data = Outbound.objects.all()
        returns_data = Returns.objects.all()
        capacity_data = Capacity.objects.all()
        inventory_data = Inventory.objects.all()

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

        # احتساب الإحصاءات الإجمالية للبيانات المصفاة
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

        # احتساب عدد السنين، الشهور، والأيام
        year_count = Inbound.objects.dates('time', 'year').count()
        month_count = Inbound.objects.dates('time', 'month').count()
        day_count = Inbound.objects.dates('time', 'day').count()

        # الحصول على جميع السنين والشهور والأيام
        years = Inbound.objects.dates('time', 'year')
        months = list(calendar.month_name)[1:]
        days = range(1, 32)  # للحصول على أيام الشهر

        # الحصول على جميع أسماء الشركات من AdminData
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

        current_user = self.request.user
        user_type = "Admin" if current_user.is_admin else "Company"
        context['current_user'] = self.request.user
        context['user_type'] = "Admin"

        return context
