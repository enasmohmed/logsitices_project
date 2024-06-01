from django.contrib import admin

from customer.models import Inbound, Company, Outbound, Returns, Expiry, Damage, \
    TravelDistance, \
    Inventory, PalletLocationAvailability, HSE

# Register your models here.


admin.site.register(Company)
admin.site.register(Inbound)
admin.site.register(Outbound)
admin.site.register(Returns)
admin.site.register(Expiry)
admin.site.register(Damage)
admin.site.register(TravelDistance)
admin.site.register(Inventory)
admin.site.register(PalletLocationAvailability)
admin.site.register(HSE)
