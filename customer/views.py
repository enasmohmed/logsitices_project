import calendar
import json

import xlwt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from administration.models import AdminData
from customer.models import CustomerInbound, CustomerOutbound, CustomerTravelDistance, CustomerExpiry, CustomerReturns, \
    CustomerInventory, CustomerHSE, CustomerDamage, \
    CustomerPalletLocationAvailability, Customer


@method_decorator(login_required, name='dispatch')
class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        context['current_user'] = self.request.user
        context['user_type'] = "Customer"

        context.update({
            'years': years,
            'months': months,
            'days': days,
        })
        return context


@login_required
@csrf_exempt
def data_entry_view(request):
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

    if request.method == 'POST':
        data = json.loads(request.body)
        if 'add' in data:
            # Handle addition logic
            pass
        elif 'update' in data:
            company = get_object_or_404(Customer, id=data['update']['id'])
            for key, value in data['update'].items():
                setattr(company, key, value)
            company.save()
        elif 'delete' in data:
            company = get_object_or_404(Customer, id=data['delete']['id'])
            company.delete()
        return JsonResponse({"success": True})

    return render(request, "excel.html", {
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
        "user": request.user,
    })


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
