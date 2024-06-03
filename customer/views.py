import calendar

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from customer.models import Inbound


@method_decorator(login_required, name='dispatch')
class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = {
            "title": "Dashboard For Customer",
            "parent": "Dashboard",
            "child": "Default"
        }

        # الحصول على جميع بيانات Inbound
        inbound_data = Inbound.objects.all()
        context['inbound_data'] = inbound_data
        context['total_shipments_in_asn'] = inbound_data.aggregate(Sum('total_shipments_in_asn'))[
                                                'total_shipments_in_asn__sum'] or 0
        context['total_arrived'] = inbound_data.aggregate(Sum('arrived'))['arrived__sum'] or 0
        context['total_no_show'] = inbound_data.aggregate(Sum('no_show'))['no_show__sum'] or 0

        context['total_received_completely'] = inbound_data.aggregate(Sum('received_completely'))[
                                                   'received_completely__sum'] or 0
        context['total_received_partially'] = inbound_data.aggregate(Sum('received_partially'))[
                                                  'received_partially__sum'] or 0
        context['total_rejected_completely'] = inbound_data.aggregate(Sum('rejected_completely'))[
                                                   'rejected_completely__sum'] or 0

        # الحصول على جميع السنين والشهور والأيام
        years = Inbound.objects.dates('time', 'year')
        months = list(calendar.month_name)[1:]
        days = range(1, 32)  # للحصول على أيام الشهر

        context['current_user'] = self.request.user
        context['user_type'] = "Customer"

        context.update({
            'years': years,
            'months': months,
            'days': days,
        })
        return context
