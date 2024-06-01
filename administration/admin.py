from django.contrib import admin

from administration.models import AdminData, Inbound, Outbound, Returns, Capacity, Inventory

# Register your models here.

admin.site.register(AdminData)
admin.site.register(Inbound)
admin.site.register(Outbound)
admin.site.register(Returns)
admin.site.register(Capacity)
admin.site.register(Inventory)
