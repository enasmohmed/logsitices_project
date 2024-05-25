# Create your views here.

from django.shortcuts import render


def index(request):
    context = {"breadcrumb": {"title": "Default Dashboard", "parent": "Dashboard", "child": "Default"}, }
    return render(request, 'index.html', context)

# def home(request):
#     owners = Owner.objects.all()
#     companies = Company.objects.all()
#     custom_users = CustomUser.objects.all()
#     inbounds = Inbound.objects.all()
#     outbounds = Outbound.objects.all()
#     returns = Returns.objects.all()
#     expiries = Expiry.objects.all()
#     damages = Damage.objects.all()
#     travel_distances = TravelDistance.objects.all()
#     inventories = Inventory.objects.all()
#     pallet_locations = PalletLocationAvailability.objects.all()
#     hse_records = HSE.objects.all()
#
#     context = {
#         'owners': owners,
#         'companies': companies,
#         'custom_users': custom_users,
#         'inbounds': inbounds,
#         'outbounds': outbounds,
#         'returns': returns,
#         'expiries': expiries,
#         'damages': damages,
#         'travel_distances': travel_distances,
#         'inventories': inventories,
#         'pallet_locations': pallet_locations,
#         'hse_records': hse_records,
#     }
#
#     return render(request, 'home.html', context)


# def make_naive_if_aware(data):
#     for item in data:
#         for key, value in item.items():
#             if isinstance(value, datetime):
#                 if is_aware(value):
#                     item[key] = make_naive(value)
#     return data


# def export_to_excel(request):
#     # جلب البيانات من جميع النماذج
#     custom_user_data = make_naive_if_aware(list(CustomUser.objects.all().values()))
#     inbound_data = make_naive_if_aware(list(Inbound.objects.all().values()))
#     outbound_data = make_naive_if_aware(list(Outbound.objects.all().values()))
#     returns_data = make_naive_if_aware(list(Returns.objects.all().values()))
#     expiry_data = make_naive_if_aware(list(Expiry.objects.all().values()))
#     damage_data = make_naive_if_aware(list(Damage.objects.all().values()))
#     travel_distance_data = make_naive_if_aware(list(TravelDistance.objects.all().values()))
#     inventory_data = make_naive_if_aware(list(Inventory.objects.all().values()))
#     pallet_location_availability_data = make_naive_if_aware(list(PalletLocationAvailability.objects.all().values()))
#     hse_data = make_naive_if_aware(list(HSE.objects.all().values()))
#
#     context = {
#         'custom_user_data': custom_user_data,
#         'inbound_data': inbound_data,
#         'outbound_data': outbound_data,
#         'returns_data': returns_data,
#         'expiry_data': expiry_data,
#         'damage_data': damage_data,
#         'travel_distance_data': travel_distance_data,
#         'inventory_data': inventory_data,
#         'pallet_location_availability_data': pallet_location_availability_data,
#         'hse_data': hse_data,
#     }
#
#     return render(request, 'export_to_excel.html', context)
