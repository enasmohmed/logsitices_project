from django.contrib import admin

from users.models import Inbound, CustomUser, Owner, Company, Outbound, Returns, Expiry

# Register your models here.

admin.site.register(Owner)
admin.site.register(Company)
admin.site.register(Inbound)
admin.site.register(Outbound)
admin.site.register(Returns)
admin.site.register(Expiry)
admin.site.register(CustomUser)
